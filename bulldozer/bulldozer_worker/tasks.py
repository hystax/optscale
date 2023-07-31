import datetime
import logging

from infra import Infra, InfraException
from name_generator import NameGenerator

LOG = logging.getLogger(__name__)

MAX_RETRIES = 20

# TODO: move to etcd
ARCEE_WAIT_TIMEOUT_SEC = 10 * 60


class ArceeWaitException(Exception):
    pass


class RunFailedException(Exception):
    pass


class DestroyConditionException(Exception):
    pass


class BudgetExceeded(DestroyConditionException):
    pass


class TimeoutConditionExceeded(DestroyConditionException):
    pass


class DestroyFlagSet(DestroyConditionException):
    pass


class GoalReached(DestroyConditionException):
    pass


class TaskState:

    STARTING_PREPARING = 1
    STARTING = 2
    STARTED = 3
    DESTROYING_SCHEDULED = 4
    DESTROY_PREPARING = 5
    DESTROYING = 6
    DESTROYED = 7
    ERROR = 9
    WAITING_ARCEE = 10


class ArceeState:
    STARTED = 1
    FINISHED = 2
    ERROR = 3
    ABORTED = 4


class RunsetState:
    CREATED = 1
    RUNNING = 2
    STOPPING = 3
    ERROR = 4
    STARTED = 5
    STOPPED = 6


class TaskReason:
    COMPLETED = "task completed successfully"


class Base:
    def __init__(
            self,
            body,
            message,
            config_cl,
            rest_cl,
            arcee_cl,
            bulldozer_cl,
            minio_cl,
            bucket_name,
            workdir,
            on_continue,
    ):
        self.message = message
        self.body = body
        self.config_cl = config_cl
        self.rest_cl = rest_cl
        self.arcee_cl = arcee_cl
        self.bulldozer_cl = bulldozer_cl
        self.minio_cl = minio_cl
        self.bucket_name = bucket_name
        self.workdir = workdir
        self.on_continue = on_continue

    def _exec(self):
        raise NotImplemented

    def check_timeout(self):
        pass

    @property
    def delayed(self):
        return False

    @staticmethod
    def _task2str(task):
        return "{state: %s,: runner_id: %s, try: %s, updated: %s}" % (
            task.get("state"),
            task.get("runner_id"),
            task.get("try"),
            str(task.get("updated"))
        )

    def update_task_state(self):
        raise NotImplementedError

    def process_infra_tries(self):
        retry = False
        # check is it spot runner type
        runner_id = self.body.get("runner_id")
        _, runner = self.bulldozer_cl.get_runner(runner_id)
        spot_settings = runner.get("spot_settings", {})
        spot_retries = spot_settings.get("tries", 0)
        if spot_retries:
            current_try = self.body.get("infra_try", 0)
            if current_try < spot_retries:
                current_try += 1
                self.body["infra_try"] = current_try
                retry = True
            elif current_try == spot_retries:
                # after # of tries fallback
                # removing _SPOT
                LOG.info("maximum %d infra retries exceeded for runner %s",
                         spot_retries, runner_id)
                c_type = self.body.get("type")
                new_type = c_type.split("_")[0]
                self.body["type"] = new_type
                retry = True
        return retry

    def should_retry(self, ex):
        # Infra exception most likely related to spot request status
        if isinstance(ex, InfraException):
            return self.process_infra_tries()

        return not isinstance(
            ex, ArceeWaitException
        ) and not isinstance(
            ex, RunFailedException
        ) and not isinstance(
            ex, DestroyConditionException
        )

    def _handle_error(self, err):
        if self.should_retry(err) and self.body["try"] < MAX_RETRIES:
            self.body["try"] += 1
        else:
            self.body["state"] = TaskState.ERROR
            self.body["reason"] = "%s" % str(err) or None
        self.on_continue(self.body, self.delayed)

    def execute(self):
        LOG.info("Task %s", self._task2str(self.body))
        try:
            self.check_timeout()
            self._exec()
        except Exception as exc:
            try:
                LOG.exception("Handling error: %s for runner %s",
                              str(exc), self.body.get("runner_id"))
                self._handle_error(exc)
            except Exception as inner_exc:
                LOG.error(
                    "Task %s failed with %s",
                    self._task2str(self.body),
                    str(inner_exc)
                )
            finally:
                self.message.ack()


class Cancel(Base):
    def _exec(self):
        pass


class Continue(Base):
    def _exec(self):
        self.on_continue(self.body, self.delayed)
        self.message.ack()


class ContinueWithDestroyConditions(Continue):

    def check_destroy_conditions(self):
        LOG.info("checking destroy conditions for task %s",
                 self._task2str(self.body))
        runner_id = self.body.get("runner_id")
        LOG.info("getting runner info for runner %s", runner_id)
        _, runner = self.bulldozer_cl.get_runner(runner_id)
        # check for destroy flag set
        if runner.get("destroy"):
            raise DestroyFlagSet("Destroy flag is set")

        destroy_conditions = runner.get("destroy_conditions", {})
        # check budget condition
        max_budget = destroy_conditions.get("max_budget", 0)
        runset_id = runner["runset_id"]
        if max_budget:
            _, runset = self.bulldozer_cl.runset_get(runset_id)
            cost = runset.get("cost", 0.0)
            LOG.info(
                "checking for budget runner %s: max: %f, current (estimated): %f",
                runner_id, max_budget, cost)
            if max_budget < cost:
                raise BudgetExceeded(
                    "Budget exceeded max: %d, current: %d" % (
                        max_budget, cost))
        max_duration = destroy_conditions.get("max_duration")
        if max_duration:
            LOG.info("checking for max duration %d for runner %s",
                     max_duration, runner_id)
            started_at = runner["started_at"]
            if started_at:
                threshold = started_at + max_duration
                now = datetime.datetime.utcnow().timestamp()
                LOG.info("runner id %s, current time: %d, threshold: %d",
                         runner_id, now, threshold)
                if now > threshold:
                    raise TimeoutConditionExceeded(
                        "Duration exceeded: current time: %d threshold: %d" % (
                            now, threshold
                        )
                    )

    def _exec(self):
        self.check_destroy_conditions()
        super()._exec()


class SetFinished(Base):

    def update_reason(self):

        reason = self.body.get("reason")
        runner_id = self.body.get('runner_id')
        _, runner = self.bulldozer_cl.get_runner(runner_id)
        run_id = runner.get("run_id")
        reason = str(reason)

        # update runner reason
        LOG.info("updating reason for runner %s, reason: %s",
                 runner_id, reason)
        _, r = self.bulldozer_cl.update_runner(
            runner_id,
            reason="%s" % reason)

        # if runner knows about arcee run, need to update it also
        if run_id:
            LOG.info("getting run info for runner: %s, run: %s",
                     runner_id, run_id)
            # update arcee run reason
            try:
                _, run = self.arcee_cl.run_get(run_id)
                run_state = run["state"]
                # In case of stared run need to abort it
                LOG.info("updating run info for run: %s (runner %s)",
                         run_id, runner_id)
                d = {"id_": run_id, "reason": reason}
                if run_state == ArceeState.STARTED:
                    run_state = ArceeState.ABORTED
                    d.update({"finish": True})
                d.update({"state": run_state})
                _, run = self.arcee_cl.run_update(
                    **d
                )
            except Exception as exc:
                LOG.exception("Updating run %s failed because of %s",
                              run_id, str(exc))


class SetSucceeded(SetFinished):

    @property
    def delayed(self):
        return True

    def _exec(self):
        self.body["reason"] = TaskReason.COMPLETED
        self.update_reason()
        LOG.info("Task %s succeeded, ACKing", self._task2str(self.body))
        self.message.ack()


class SetFailed(SetFinished):
    def _exec(self):
        LOG.info("Task %s failed, ACKing", self._task2str(self.body))
        # set failed state in API
        runner_id = self.body.get('runner_id')
        # Ensure infra is deleted
        try:
            LOG.info("Entering error state for runner %s", runner_id)
            _, runner = self.bulldozer_cl.get_runner(runner_id)
            cloud_account_id = runner["cloud_account_id"]
            _, cloud_account = self.rest_cl.cloud_account_get(cloud_account_id, True)
            c_type = self.body.get("type")
            infra = Infra(
                runner_id,
                c_type,
                self.minio_cl,
                self.bucket_name,
                self.workdir,
                creds={
                    "aws_access_key_id": cloud_account["config"]["access_key_id"],
                    "aws_secret_access_key": cloud_account["config"]["secret_access_key"]
                }
            )
            infra.destroy()

        except Exception as exc:
            # basically exception
            LOG.exception("Cleanup problem: %s", str(exc))
        finally:
            _, r = self.bulldozer_cl.update_runner(
                runner_id,
                state=TaskState.ERROR,
                destroyed_at=int(datetime.datetime.utcnow().timestamp()))
            self.update_reason()
        self.message.ack()


class StartInfra(Continue):

    @property
    def delayed(self):
        return True

    def update_task_state(self):
        self.body['state'] = TaskState.WAITING_ARCEE

    def _exec(self):
        runner_id = self.body.get('runner_id')
        LOG.info("processing starting runner %s" % runner_id)
        _, runner = self.bulldozer_cl.get_runner(runner_id)
        cloud_account_id = runner["cloud_account_id"]
        prefix = runner.get("name_prefix", "")
        user_data = ""
        hp = runner.get("hyperparameters")
        commands = runner.get("commands")
        instance_type = runner["instance_type"]
        region_id = runner["region_id"]
        tags = runner.get("tags", dict())
        # opens ingress ports for runner instance
        open_ingress = runner.get("open_ingress", False)

        if hp is not None and isinstance(hp, dict):
            for k, v in hp.items():
                user_data += "export %s=%s\n" % (k, v)
        if commands is not None:
            user_data += commands
        name = "%s_%s" % (prefix, NameGenerator.get_random_name())
        _, r = self.bulldozer_cl.update_runner(
            runner_id,
            state=TaskState.STARTING,
            name=name)
        _, cloud_account = self.rest_cl.cloud_account_get(cloud_account_id, True)
        # TODO: get cloud type form cloud account to support multi-cloud
        # Now only AWS is supported
        c_type = "AWS"
        if not self.body.get("type"):
            # if we have spot settings we should try spot instances first
            if bool(runner.get("spot_settings")):
                c_type = "%s_%s" % (c_type, "SPOT")
                LOG.info("spot settings found, new type: %s, runner: %s",
                         c_type, runner_id)
            self.body["type"] = c_type
        infra = Infra(
            runner_id,
            c_type,
            self.minio_cl,
            self.bucket_name,
            self.workdir,
            creds={
                "aws_access_key_id": cloud_account["config"]["access_key_id"],
                "aws_secret_access_key": cloud_account["config"]["secret_access_key"]
            }
        )
        LOG.info("starting infra for runner %s with user data: %s", runner_id, user_data)

        id_, ip_addr = infra.start(
            name,
            region_id,
            instance_type,
            20,
            user_data,
            image=None,  # using default image
            key=None,
            tags=tags,
            open_ingress=open_ingress,
        )

        LOG.info("Created runner id=%s, instance=%s, ip=%s", runner_id, id_, ip_addr)
        # update runner in bulldozer API
        _, r = self.bulldozer_cl.update_runner(
            runner_id,
            state=TaskState.WAITING_ARCEE,
            started_at=int(datetime.datetime.utcnow().timestamp()),
            instance_id=id_,
            ip_addr=ip_addr,
            return_code=0
        )
        self.body["updated"] = int(datetime.datetime.utcnow().timestamp())
        self.update_task_state()
        super()._exec()


class WaitArcee(ContinueWithDestroyConditions):
    @property
    def delayed(self):
        return True

    def update_task_state(self):
        self.body['state'] = TaskState.STARTED

    def _exec(self):
        runner_id = self.body.get('runner_id')
        LOG.info("starting waiting arcee for runner %s", runner_id)
        _, runner = self.bulldozer_cl.get_runner(runner_id)
        LOG.info("got runner from bulldozer API: %s", runner)
        instance_id = runner["instance_id"]
        application_id = runner["application_id"]
        hp = runner["hyperparameters"]
        runset_id = runner["runset_id"]
        _, runset = self.bulldozer_cl.runset_get(runset_id)
        runset_name = runset.get("name", "")

        LOG.info("checking for arcee runs for executor: %s", instance_id)
        # try to get run id from Arcee
        _, runs = self.arcee_cl.runs_by_executor(instance_id, [application_id])
        LOG.info("runs info: %s", str(runs))

        if not runs:
            # check timeout
            last_updated = int(self.body.get("updated"))
            current_time = int(datetime.datetime.utcnow().timestamp())
            wait_time = last_updated + ARCEE_WAIT_TIMEOUT_SEC
            LOG.info("runs not found. current time: %d, wait time: %s",
                     current_time, wait_time)
            if current_time > wait_time:
                # TODO: Do we need automatically destroy env?
                raise ArceeWaitException("Arcee wait exceeded")
        else:
            run_id = runs[0]
            LOG.info("run found! run id: %s", run_id)
            LOG.info("updating run %s with runset id %s", run_id, runset_id)
            # update run
            _, run = self.arcee_cl.run_update(
                run_id,
                runset_id=runset_id,
                runset_name=runset_name,
                hyperparameters=hp,
            )
            _, r = self.bulldozer_cl.update_runner(
                runner_id,
                run_id=run_id,
                state=TaskState.STARTED,
            )
            self.body["updated"] = int(datetime.datetime.utcnow().timestamp())
            self.update_task_state()
        super()._exec()


class Stop(Continue):

    @property
    def delayed(self):
        return True

    def update_task_state(self):
        self.body['state'] = TaskState.DESTROYED

    def _exec(self):
        runner_id = self.body.get('runner_id')
        LOG.info("starting task destroying runner: %s", runner_id)
        _, r = self.bulldozer_cl.update_runner(
            runner_id,
            state=TaskState.DESTROYING,
        )
        _, runner = self.bulldozer_cl.get_runner(runner_id)
        cloud_account_id = runner["cloud_account_id"]
        _, cloud_account = self.rest_cl.cloud_account_get(cloud_account_id, True)
        infra = Infra(
            runner_id,
            "AWS",
            self.minio_cl,
            self.bucket_name,
            self.workdir,
            creds={
                "aws_access_key_id": cloud_account["config"]["access_key_id"],
                "aws_secret_access_key": cloud_account["config"]["secret_access_key"]
            }
        )
        try:
            infra.destroy()
        except Exception as exc:
            LOG.error("error executing terraform for runner %s: %s", runner_id, str(exc))
        finally:
            # update runner
            _, r = self.bulldozer_cl.update_runner(
                runner_id,
                state=TaskState.DESTROYED,
                destroyed_at=int(datetime.datetime.utcnow().timestamp())
            )
        self.body["updated"] = int(datetime.datetime.utcnow().timestamp())
        self.update_task_state()
        super()._exec()


class WaitRun(ContinueWithDestroyConditions):

    @property
    def delayed(self):
        return True

    def update_task_state(self):
        self.body['state'] = TaskState.DESTROYING_SCHEDULED

    def check_goals_reached(self, runner, run):
        runner_id = runner["_id"]
        runset_id = runner["runset_id"]
        destroy_conditions = runner.get("destroy_conditions", {})
        reached_goals = destroy_conditions.get("reached_goals")
        if reached_goals:
            LOG.info("checking for reached goals for runner %s", runner_id)
            run_id = runner.get("run_id")
            # ensure run id is set for runner
            if not run_id:
                LOG.info("run not found for runner %s, skipping", runner_id)
            else:
                goals = run.get('reached_goals', {})
                LOG.info('goals for run %s (runner %s) goals: %s',
                         run_id, runner_id, str(goals))
                reached = bool(goals) and all(map(lambda x: x.get("reached", False), goals.values()))
                if reached:
                    LOG.info("reached goal for run %s, runner id: %s",
                             run_id, runner_id)
                    LOG.info("will mark runset %s to stop", runset_id)
                    _, runner = self.bulldozer_cl.runset_update(
                        runset_id,
                        state=RunsetState.STOPPED,
                        runner_id=runner_id,
                    )

    def _exec(self):
        runner_id = self.body.get('runner_id')
        LOG.info("starting waiting arcee run for runner %s", runner_id)
        _, runner = self.bulldozer_cl.get_runner(runner_id)
        LOG.info("got runner from bulldozer API: %s", runner)
        run_id = runner["run_id"]
        LOG.info("Checking run state with Arcee for run id %s", run_id)
        _, run = self.arcee_cl.run_get(run_id)
        state = run["state"]
        LOG.info("Got arcee run: %s", str(run))
        if state == ArceeState.FINISHED:
            LOG.info("Run %s completed by runner %s checking for reached goals if set",
                     run_id, runner_id)
            self.check_goals_reached(runner, run)
            # if state is finished need to schedule destroying runner
            LOG.info("Run %s completed, scheduling destroying runner %s infra",
                     run_id, runner_id)
            _, r = self.bulldozer_cl.update_runner(
                runner_id,
                state=TaskState.DESTROYING_SCHEDULED)
            self.update_task_state()
        elif state == ArceeState.ERROR:
            LOG.info("Run %s failed, setting runner %s error state",
                     run_id, runner_id)
            raise RunFailedException("Run %s failed for runner %s" % (
                                     run_id, runner_id))
        super()._exec()

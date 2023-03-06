/* eslint-disable no-underscore-dangle */
import { applications } from "./applications";
import { executors } from "./executors";
import { executorsBreakdown } from "./executorsBreakdown";
import { runBreakdowns } from "./runBreakdown";
import { runs } from "./runs";

const _getApplicationRuns = (applicationId) => runs.filter(({ application_id: id }) => id === applicationId);

const _getApplicationExecutors = (applicationId) =>
  executors.filter(({ applicationIds }) => applicationIds.includes(applicationId));

const getApplicationExecutors = () => _getApplicationExecutors("1e0815a2-72d2-418b-afad-bedc99a5e9d2");

const getRunExecutors = (runId) => executors.filter(({ runIds }) => runIds.includes(runId));

const _getApplicationInfo = (applicationId) => {
  const applicationRuns = _getApplicationRuns(applicationId);

  if (applicationRuns.length !== 0) {
    const lastRun = applicationRuns[0];

    const applicationExecutors = getApplicationExecutors(applicationId);

    const lastRunExecutors = getRunExecutors(lastRun.id);

    const last30DaysCost = applicationRuns.reduce((acc, curr) => acc + curr.cost, 0);

    return {
      last_run: lastRun.start,
      last_run_cost: lastRun.cost,
      last_run_duration: lastRun.duration,
      last_run_executor: lastRunExecutors.length !== 0 ? lastRunExecutors[0] ?? null : null,
      last_successful_run: lastRun.start,
      run_goals: lastRun.goals.map((goal) => ({
        ...goal,
        last_run_value: lastRun.data[goal.key],
        history: applicationRuns.map((run) => run.data[goal.key]).reverse()
      })),
      executors: applicationExecutors,
      executors_count: applicationExecutors.length,
      runs_count: applicationRuns.length,
      last_30_days_cost: last30DaysCost,
      total_cost: last30DaysCost * 2.5
    };
  }

  return {
    last_run: 0,
    last_run_cost: 0,
    last_run_duration: 0,
    last_run_executor: null,
    last_successful_run: 0,
    run_goals: [],
    executors: [],
    executors_count: 0,
    runs_count: 0,
    total_cost: 0,
    last_30_days_cost: 0
  };
};

const getApplication = (applicationId) => applications.find(({ id }) => id === applicationId);

const _getApplicationDetails = (applicationId) => {
  const application = getApplication(applicationId);

  if (application) {
    return {
      ...application,
      ..._getApplicationInfo(application.id)
    };
  }

  return {};
};

const getApplicationsDetails = () =>
  applications.map((application) => ({
    ...application,
    ..._getApplicationInfo(application.id)
  }));

const getRunDetails = (runId) => {
  const run = runs.find(({ id }) => id === runId);

  if (run) {
    return {
      ...run,
      application: getApplication(run.application_id)
    };
  }

  return {};
};

const getRunBreakdown = (runId) =>
  runBreakdowns[runId] ?? {
    breakdown: {},
    milestones: [],
    stages: []
  };

const getApplicationDetails = () => _getApplicationDetails("1e0815a2-72d2-418b-afad-bedc99a5e9d2");

const getApplicationRuns = () => _getApplicationRuns("1e0815a2-72d2-418b-afad-bedc99a5e9d2");

const getExecutorsBreakdown = (breakdownBy) => executorsBreakdown[breakdownBy] ?? {};

const getExecutors = () => executors;

export {
  getApplicationsDetails,
  getRunDetails,
  getRunBreakdown,
  getRunExecutors,
  getApplicationDetails,
  getApplicationExecutors,
  getApplicationRuns,
  getExecutorsBreakdown,
  getExecutors
};

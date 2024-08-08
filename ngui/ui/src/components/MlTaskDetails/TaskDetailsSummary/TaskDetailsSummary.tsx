import SettingsIcon from "@mui/icons-material/Settings";
import { Box, Stack } from "@mui/material";
import { FormattedMessage, FormattedNumber } from "react-intl";
import { useNavigate } from "react-router-dom";
import CloudLabel from "components/CloudLabel";
import ExecutorLabel from "components/ExecutorLabel";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import LastTaskRunGoals from "components/LastTaskRunGoals";
import Markdown from "components/Markdown";
import ModeWrapper from "components/ModeWrapper";
import SummaryList from "components/SummaryList";
import TypographyLoader from "components/TypographyLoader";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { getEditMlTaskUrl } from "urls";
import { ML_TASK_DETAILS_TAB_NAME, OPTSCALE_MODE } from "utils/constants";
import { getTimeDistance } from "utils/datetime";
import { SPACING_2 } from "utils/layouts";
import { getQueryParams } from "utils/network";
import { isEmpty as isEmptyObject } from "utils/objects";

const LastRunExecutorSummary = ({ isLoading, lastRunExecutor }) => {
  const { isDemo } = useOrganizationInfo();

  const {
    instance_region: instanceRegion,
    instance_id: instanceId,
    instance_type: instanceType,
    platform_type: platformType,
    resource,
    discovered
  } = lastRunExecutor ?? {};

  return (
    <SummaryList
      titleMessage={<FormattedMessage id="lastRunExecutor" />}
      isLoading={isLoading}
      items={[
        lastRunExecutor && (
          <ExecutorLabel
            key="executor_label"
            discovered={discovered}
            resource={resource}
            instanceId={instanceId}
            platformType={platformType}
          />
        ),
        <KeyValueLabel
          key="cloud"
          keyMessageId="cloud"
          value={
            resource && resource.cloud_account ? (
              <CloudLabel
                disableLink={isDemo}
                id={resource.cloud_account.id}
                name={resource.cloud_account.name}
                type={resource.cloud_account.type}
              />
            ) : undefined
          }
        />,
        <KeyValueLabel key="name" keyMessageId="name" value={resource?.name} />,
        <KeyValueLabel key="region" keyMessageId="region" value={instanceRegion} />,
        <KeyValueLabel key="size" keyMessageId="size" value={instanceType} />
      ]}
    />
  );
};

const SummaryInfo = ({
  taskId,
  taskKey,
  lastRunReachedGoals,
  lastRunMetrics,
  runsCount,
  isLoading,
  lastSuccessfulRunTimestamp,
  lastRunCost,
  ownerName,
  lastRunExecutor
}) => {
  const navigate = useNavigate();

  return (
    <Box display="flex" flexWrap="wrap" rowGap={1} columnGap={16}>
      <Box>
        <SummaryList
          titleMessage={<FormattedMessage id="trackedMetrics" />}
          titleIconButton={{
            icon: <SettingsIcon fontSize="small" />,
            onClick: () => {
              const { [ML_TASK_DETAILS_TAB_NAME]: mlTaskDetailsTabName } = getQueryParams();
              navigate(
                getEditMlTaskUrl(taskId, {
                  tab: "metrics",
                  [ML_TASK_DETAILS_TAB_NAME]: mlTaskDetailsTabName
                })
              );
            }
          }}
          isLoading={isLoading}
          items={
            isEmptyObject(lastRunReachedGoals) ? (
              <FormattedMessage id="thereAreNoMetricsDefinedForTask" />
            ) : (
              <LastTaskRunGoals lastRunMetrics={lastRunMetrics} taskReachedGoals={lastRunReachedGoals} />
            )
          }
        />
      </Box>
      <Box>
        <SummaryList
          titleMessage={<FormattedMessage id="summary" />}
          isLoading={isLoading}
          items={[
            <KeyValueLabel key="key" keyMessageId="key" value={taskKey} />,
            <KeyValueLabel key="runs" keyMessageId="runs" value={<FormattedNumber value={runsCount} />} />,
            <KeyValueLabel
              key="lastSuccessfulRun"
              keyMessageId="lastSuccessfulRun"
              value={
                <FormattedMessage
                  id={lastSuccessfulRunTimestamp === 0 ? "never" : "valueAgo"}
                  values={{
                    value: lastSuccessfulRunTimestamp ? getTimeDistance(lastSuccessfulRunTimestamp) : null
                  }}
                />
              }
            />,
            <ModeWrapper key="lastRunCost" mode={OPTSCALE_MODE.FINOPS}>
              <KeyValueLabel keyMessageId="lastRunCost" value={<FormattedMoney value={lastRunCost} />} />
            </ModeWrapper>,
            <KeyValueLabel key="owner" keyMessageId="owner" value={ownerName} />
          ]}
        />
      </Box>
      <Box>
        <LastRunExecutorSummary isLoading={isLoading} lastRunExecutor={lastRunExecutor} />
      </Box>
    </Box>
  );
};

const TaskDetailsSummary = ({ task, isTaskDetailsLoading = false }) => {
  const {
    id: taskId,
    key: taskKey,
    description,
    last_run_cost: lastRunCost = 0,
    run_metrics: lastRunMetrics = [],
    owner: { name: ownerName } = {},
    last_successful_run: lastSuccessfulRunTimestamp,
    runs_count: runsCount = 0,
    last_run_executor: lastRunExecutor,
    last_run_reached_goals: lastRunReachedGoals = {}
  } = task;

  return (
    <Stack spacing={SPACING_2}>
      {isTaskDetailsLoading ? (
        <TypographyLoader linesCount={4} />
      ) : (
        description && (
          <div>
            <Markdown>{description}</Markdown>
          </div>
        )
      )}
      <div>
        <SummaryInfo
          taskId={taskId}
          taskKey={taskKey}
          lastRunReachedGoals={lastRunReachedGoals}
          lastRunMetrics={lastRunMetrics}
          runsCount={runsCount}
          isLoading={isTaskDetailsLoading}
          lastSuccessfulRunTimestamp={lastSuccessfulRunTimestamp}
          lastRunCost={lastRunCost}
          ownerName={ownerName}
          lastRunExecutor={lastRunExecutor}
        />
      </div>
    </Stack>
  );
};

export default TaskDetailsSummary;

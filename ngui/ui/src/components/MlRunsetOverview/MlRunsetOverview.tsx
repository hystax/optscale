import { useState } from "react";
import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import StopCircleOutlinedIcon from "@mui/icons-material/StopCircleOutlined";
import { Link, Stack, Typography } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import { GET_ML_RUNSET, GET_ML_RUNSETS_RUNS, GET_ML_RUNSET_EXECUTORS } from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import PageContentWrapper from "components/PageContentWrapper";
import Skeleton from "components/Skeleton";
import TypographyLoader from "components/TypographyLoader";
import { useRefetchApis } from "hooks/useRefetchApis";
import { ML_RUNSET_TEMPLATES, getMlTaskDetailsUrl, getMlRunsetTemplateUrl } from "urls";
import { getColorScale } from "utils/charts";
import { SPACING_1 } from "utils/layouts";
import { formatRunFullName } from "utils/ml";
import { InputParameters, SummaryCards, Tabs } from "./Components";
import Correlations from "./Components/Correlations";

const MlRunsetOverview = ({
  runset,
  runsetRuns,
  stopRunset,
  isGetRunsetLoading = false,
  isGetRunsetRunsLoading = false,
  isStopMlRunsetLoading = false
}) => {
  const theme = useTheme();
  const refetch = useRefetchApis();

  const {
    name: runsetName,
    template: { name: runsetTemplateName, id: runsetTemplateId } = {},
    number: runsetNumber,
    task: { id: taskId, name: taskName, deleted: isTaskDeleted = false } = {},
    runs_count: runsCount = 0,
    succeeded_runs: completedRuns = 0,
    cost = 0,
    destroyed_at: destroyedAt
  } = runset;

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={ML_RUNSET_TEMPLATES} component={RouterLink}>
        <FormattedMessage id="runsetTemplatesTitle" />
      </Link>,
      <Link key={2} to={getMlRunsetTemplateUrl(runsetTemplateId)} component={RouterLink}>
        {runsetTemplateName}
      </Link>,
      <FormattedMessage key={3} id="runsets" />
    ],
    title: {
      isLoading: isGetRunsetLoading,
      text: <Typography>{formatRunFullName(runsetNumber, runsetName)}</Typography>
    },
    items: [
      {
        key: "btn-refresh",
        icon: <RefreshOutlinedIcon fontSize="small" />,
        messageId: "refresh",
        dataTestId: "btn_refresh",
        type: "button",
        action: () => refetch([GET_ML_RUNSET, GET_ML_RUNSETS_RUNS, GET_ML_RUNSET_EXECUTORS])
      },
      {
        key: "btn-stop",
        icon: <StopCircleOutlinedIcon fontSize="small" />,
        messageId: "stop",
        dataTestId: "btn_stop",
        type: "button",
        action: stopRunset,
        show: isGetRunsetLoading || destroyedAt === 0,
        isLoading: isGetRunsetLoading || isStopMlRunsetLoading,
        tooltip: {
          show: true,
          messageId: "stopRunsetButtonDescription"
        }
      }
    ]
  };

  const [selectedRunNumbers, setSelectedRunNumbers] = useState();

  const colorScale = getColorScale(theme.palette.chart);

  const runs = runsetRuns.map((run, index) => ({
    ...run,
    index,
    color: colorScale(index)
  }));

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Stack spacing={SPACING_1}>
          <div>
            <SummaryCards isLoading={isGetRunsetLoading} runsCount={runsCount} completedRuns={completedRuns} cost={cost} />
          </div>
          <div>
            {isGetRunsetLoading ? (
              <TypographyLoader rowsCount={1} />
            ) : (
              <KeyValueLabel
                keyMessageId="task"
                value={
                  isTaskDeleted ? (
                    taskName
                  ) : (
                    <Link to={getMlTaskDetailsUrl(taskId)} component={RouterLink}>
                      {taskName}
                    </Link>
                  )
                }
              />
            )}
          </div>
          <div>
            <InputParameters runset={runset} isLoading={isGetRunsetLoading} />
          </div>
          <div>
            {isGetRunsetRunsLoading ? (
              <Skeleton fullWidth variant="rectangular">
                <Correlations runs={runs} />
              </Skeleton>
            ) : (
              <Correlations runs={runs} setSelectedRunNumbers={setSelectedRunNumbers} />
            )}
          </div>
          <div>
            <Tabs
              runs={selectedRunNumbers === undefined ? runs : runs.filter(({ number }) => selectedRunNumbers.includes(number))}
              isGetRunsetRunsLoading={isGetRunsetRunsLoading}
            />
          </div>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default MlRunsetOverview;

import { useMemo } from "react";
import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import ActionBar from "components/ActionBar";
import LeaderboardForm from "components/LeaderboardForm";
import { getDefaultValues } from "components/LeaderboardForm/utils";
import PageContentWrapper from "components/PageContentWrapper";
import { ML_TASKS, getMlTaskDetailsUrl } from "urls";

const SetupLeaderboard = ({ task, runs, datasetLabels, onSetup, isLoadingProps = {} }) => {
  const navigate = useNavigate();

  const { id, name } = task;
  const {
    isGetTaskLoading = false,
    isGetRunsListLoading = false,
    isSetupLoading = false,
    isGetDatasetLabelsLoading = false
  } = isLoadingProps;

  const mlTaskDetailsUrl = getMlTaskDetailsUrl(id);

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={ML_TASKS} component={RouterLink}>
        <FormattedMessage id="tasks" />
      </Link>,
      <Link key={2} to={mlTaskDetailsUrl} component={RouterLink}>
        {name}
      </Link>
    ],
    title: {
      text: <FormattedMessage id="setupLeaderboardTemplateTitle" />,
      dataTestId: "lbl_setup_leaderboard",
      isLoading: isGetTaskLoading
    }
  };

  const runTags = useMemo(() => Array.from(new Set(runs.flatMap((run) => Object.keys(run.tags)))), [runs]);

  const defaultValues = useMemo(
    () =>
      getDefaultValues({
        tags: runTags,
        groupByHyperparameters: true,
        metricRestrictions: [
          {
            max: "",
            min: "",
            id: ""
          }
        ],
        datasetCoverageRules: {
          "": ""
        }
      }),
    [runTags]
  );

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Box
          sx={{
            width: { md: "50%" }
          }}
        >
          <LeaderboardForm
            defaultValues={defaultValues}
            onSubmit={onSetup}
            onCancel={() => navigate(mlTaskDetailsUrl)}
            runTags={runTags}
            metrics={task.metrics}
            datasetLabels={datasetLabels}
            isTemplate
            isLoadingProps={{
              isGetDataLoading: isGetTaskLoading || isGetRunsListLoading || isGetDatasetLabelsLoading,
              isSubmitDataLoading: isSetupLoading
            }}
          />
        </Box>
      </PageContentWrapper>
    </>
  );
};

export default SetupLeaderboard;

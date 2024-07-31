import { useMemo } from "react";
import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import ActionBar from "components/ActionBar";
import LeaderboardForm from "components/LeaderboardForm";
import { getDefaultValues } from "components/LeaderboardForm/utils";
import PageContentWrapper from "components/PageContentWrapper";
import { ML_TASKS, getMlTaskDetailsUrl } from "urls";

const SetupLeaderboard = ({ task, datasetLabels, groupingTags, onSetup, isLoadingProps = {} }) => {
  const navigate = useNavigate();

  const { id, name } = task;
  const {
    isGetTaskLoading = false,
    isGetTaskTagsLoading = false,
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

  const defaultValues = useMemo(
    () =>
      getDefaultValues({
        tags: groupingTags,
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
    [groupingTags]
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
            groupingTags={groupingTags}
            metrics={task.metrics}
            datasetLabels={datasetLabels}
            isTemplate
            isLoadingProps={{
              isGetDataLoading: isGetTaskLoading || isGetTaskTagsLoading || isGetDatasetLabelsLoading,
              isSubmitDataLoading: isSetupLoading
            }}
          />
        </Box>
      </PageContentWrapper>
    </>
  );
};

export default SetupLeaderboard;

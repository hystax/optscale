import React, { useMemo } from "react";
import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import SetupLeaderboardsForm, {
  defaultValues as setupLeaderboardDefaultValues,
  FIELD_NAMES
} from "components/SetupLeaderboardsForm";
import { ML_TASKS, getMlModelDetailsUrl } from "urls";

const SetupLeaderboard = ({ task, runs, onSetup, isLoadingProps = {} }) => {
  const navigate = useNavigate();

  const { id, name } = task;
  const { isGetTaskLoading = false, isGetRunsListLoading = false, isSetupLoading = false } = isLoadingProps;

  const mlModelDetailsUrl = getMlModelDetailsUrl(id);

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={ML_TASKS} component={RouterLink}>
        <FormattedMessage id="tasks" />
      </Link>,
      <Link key={2} to={mlModelDetailsUrl} component={RouterLink}>
        {name}
      </Link>
    ],
    title: {
      text: <FormattedMessage id="setupLeaderboards" />,
      dataTestId: "lbl_setup_leaderboard",
      isLoading: isGetTaskLoading || isGetRunsListLoading
    }
  };

  const runTags = useMemo(() => Array.from(new Set(runs.flatMap((run) => Object.keys(run.tags)))), [runs]);

  const defaultValues = useMemo(
    () => ({
      ...setupLeaderboardDefaultValues,
      [FIELD_NAMES.RUN_TAGS_FIELD_NAME]: runTags
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
          <SetupLeaderboardsForm
            metrics={task.goals}
            runTags={runTags}
            isLoadingProps={{
              isGetDataLoading: isGetTaskLoading || isGetRunsListLoading,
              isSubmitDataLoading: isSetupLoading
            }}
            onSubmit={onSetup}
            defaultValues={defaultValues}
            onCancel={() => navigate(mlModelDetailsUrl)}
          />
        </Box>
      </PageContentWrapper>
    </>
  );
};

export default SetupLeaderboard;

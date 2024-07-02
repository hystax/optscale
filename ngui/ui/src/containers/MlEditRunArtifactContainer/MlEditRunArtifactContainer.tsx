import { Box, Link, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useParams, Link as RouterLink, useNavigate } from "react-router-dom";
import ActionBar from "components/ActionBar";
import { MlEditArtifactForm } from "components/forms/MlArtifactForm";
import { TABS } from "components/MlTaskRun";
import PageContentWrapper from "components/PageContentWrapper";
import MlArtifactsService from "services/MlArtifactsService";
import MlTasksService from "services/MlTasksService";
import { ML_TASKS, getMlTaskDetailsUrl, getMlTaskRunUrl } from "urls";
import { formatRunFullName } from "utils/ml";

const MlEditRunArtifactContainer = () => {
  const { runId, taskId, artifactId } = useParams() as { artifactId: string; taskId: string; runId: string };
  const navigate = useNavigate();

  const { useGetOne, useUpdate } = MlArtifactsService();
  const { useGetTaskRun } = MlTasksService();

  const { isLoading: isGetArtifactLoading, artifact } = useGetOne(artifactId);
  const { name: artifactName } = artifact;

  const { isLoading: isUpdateArtifactLoading, onUpdate } = useUpdate();

  const { isLoading: isGetRunLoading, run } = useGetTaskRun(runId);
  const { name: runName, number: runNumber, task: { name: taskName = "" } = {} } = run;

  const taskDetailsUrl = getMlTaskDetailsUrl(taskId);
  const taskRunUrl = getMlTaskRunUrl(taskId, runId, { tab: TABS.ARTIFACTS });

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={ML_TASKS} component={RouterLink}>
        <FormattedMessage id="tasks" />
      </Link>,
      <Link key={2} to={taskDetailsUrl} component={RouterLink}>
        {taskName}
      </Link>,
      <FormattedMessage key={3} id="runs" />,
      <Link key={4} to={taskRunUrl} component={RouterLink}>
        {formatRunFullName(runNumber, runName)}
      </Link>,
      <FormattedMessage key={4} id="artifacts" />,
      <Typography key={5}>{artifactName}</Typography>
    ],
    title: {
      isLoading: isGetArtifactLoading || isGetRunLoading,
      messageId: "editArtifactTitle"
    }
  };

  const redirect = () => navigate(taskRunUrl);

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Box
          sx={{
            width: { md: "50%" }
          }}
        >
          <MlEditArtifactForm
            artifact={artifact}
            onSubmit={(formData) => onUpdate(artifactId, formData).then(redirect)}
            onCancel={redirect}
            isLoadingProps={{ isGetArtifactLoading, isUpdateArtifactLoading }}
          />
        </Box>
      </PageContentWrapper>
    </>
  );
};

export default MlEditRunArtifactContainer;

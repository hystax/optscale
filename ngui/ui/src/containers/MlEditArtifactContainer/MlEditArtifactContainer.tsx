import { Box, Link, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useParams, Link as RouterLink, useNavigate } from "react-router-dom";
import ActionBar from "components/ActionBar";
import { MlEditArtifactForm } from "components/forms/MlArtifactForm";
import PageContentWrapper from "components/PageContentWrapper";
import MlArtifactsService from "services/MlArtifactsService";
import { ML_ARTIFACTS } from "urls";

const MlEditArtifactContainer = () => {
  const { artifactId } = useParams() as { artifactId: string; taskId: string; runId: string };
  const navigate = useNavigate();

  const { useGetOne, useUpdate } = MlArtifactsService();

  const { isLoading: isGetArtifactLoading, artifact } = useGetOne(artifactId);
  const { name: artifactName } = artifact;

  const { isLoading: isUpdateArtifactLoading, onUpdate } = useUpdate();

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={ML_ARTIFACTS} component={RouterLink}>
        <FormattedMessage id="artifacts" />
      </Link>,
      <Typography key={5}>{artifactName}</Typography>
    ],
    title: {
      isLoading: isGetArtifactLoading,
      messageId: "editArtifactTitle"
    }
  };

  const redirect = () => navigate(ML_ARTIFACTS);

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

export default MlEditArtifactContainer;

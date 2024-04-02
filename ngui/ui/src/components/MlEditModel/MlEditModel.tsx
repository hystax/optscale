import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import MlEditModelFormContainer from "containers/MlEditModelFormContainer";
import { ModelDetails } from "services/MlModelsService";
import { ML_MODELS, getMlModelUrl } from "urls";

type MlEditModelProps = {
  model: ModelDetails;
  isLoading: boolean;
};

const MlEditModel = ({ model, isLoading }: MlEditModelProps) => {
  const { id, name } = model;

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={ML_MODELS} component={RouterLink}>
        <FormattedMessage id="models" />
      </Link>,
      <Link key={2} to={getMlModelUrl(id)} component={RouterLink}>
        {name}
      </Link>
    ],
    title: {
      messageId: "editModelTitle",
      isLoading,
      dataTestId: "lbl_edit_model"
    }
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Box
          sx={{
            width: { md: "50%" }
          }}
        >
          <MlEditModelFormContainer model={model} isModelLoading={isLoading} />
        </Box>
      </PageContentWrapper>
    </>
  );
};

export default MlEditModel;

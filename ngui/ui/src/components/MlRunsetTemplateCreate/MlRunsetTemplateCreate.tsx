import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import MlRunsetTemplateCreateFormContainer from "containers/MlRunsetTemplateCreateFormContainer";
import { ML_RUNSET_TEMPLATES } from "urls";

const actionBarDefinition = {
  breadcrumbs: [
    <Link key={1} to={ML_RUNSET_TEMPLATES} component={RouterLink}>
      <FormattedMessage id="runsetTemplatesTitle" />
    </Link>
  ],
  title: {
    messageId: "addRunsetTemplateTitle",
    dataTestId: "lbl_add_runset_template"
  }
};

const MlRunsetTemplateCreate = () => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <Box
        sx={{
          width: { md: "50%" }
        }}
      >
        <MlRunsetTemplateCreateFormContainer />
      </Box>
    </PageContentWrapper>
  </>
);

export default MlRunsetTemplateCreate;

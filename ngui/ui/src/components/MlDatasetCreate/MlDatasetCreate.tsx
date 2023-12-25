import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import MlDatasetCreateFormContainer from "containers/MlDatasetCreateFormContainer";
import { ML_DATASETS } from "urls";

const actionBarDefinition = {
  breadcrumbs: [
    <Link key={1} to={ML_DATASETS} component={RouterLink}>
      <FormattedMessage id="datasets" />
    </Link>
  ],
  title: {
    messageId: "addDatasetTitle",
    dataTestId: "lbl_add_dataset"
  }
};

const MlDatasetCreate = () => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <Box
        sx={{
          width: { md: "50%" }
        }}
      >
        <MlDatasetCreateFormContainer />
      </Box>
    </PageContentWrapper>
  </>
);

export default MlDatasetCreate;

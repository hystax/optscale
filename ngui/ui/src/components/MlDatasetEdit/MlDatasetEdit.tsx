import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import { MlDatasetEditForm } from "components/MlDatasetForm";
import PageContentWrapper from "components/PageContentWrapper";
import { ML_DATASETS } from "urls";

const MlDatasetEdit = ({ dataset, onSubmit, onCancel, isLoadingProps }) => {
  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={ML_DATASETS} component={RouterLink}>
        <FormattedMessage id="datasets" />
      </Link>,
      <span key={2}>{dataset.name}</span>
    ],
    title: {
      messageId: "editDatasetTitle",
      dataTestId: "lbl_edit_dataset"
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
          <MlDatasetEditForm dataset={dataset} onSubmit={onSubmit} onCancel={onCancel} isLoadingProps={isLoadingProps} />
        </Box>
      </PageContentWrapper>
    </>
  );
};

export default MlDatasetEdit;

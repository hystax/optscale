import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import BIExportForm from "components/forms/BIExportForm";
import { getDefaultValues } from "components/forms/BIExportForm/utils";
import PageContentWrapper from "components/PageContentWrapper";
import { BI_EXPORTS, INTEGRATIONS } from "urls";

const defaultValues = getDefaultValues();

const CreateBIExport = ({ onSubmit, onCancel, isLoadingProps }) => (
  <>
    <ActionBar
      data={{
        breadcrumbs: [
          <Link key={1} to={INTEGRATIONS} component={RouterLink}>
            <FormattedMessage id="integrations" />
          </Link>,
          <Link key={2} to={BI_EXPORTS} component={RouterLink}>
            <FormattedMessage id="biExportTitle" />
          </Link>
        ],
        title: {
          messageId: "createBIExportTitle",
          dataTestId: "lbl_create_bi_export_title"
        }
      }}
    />
    <PageContentWrapper>
      <Box
        sx={{
          width: { md: "50%" }
        }}
      >
        <BIExportForm defaultValues={defaultValues} isLoadingProps={isLoadingProps} onSubmit={onSubmit} onCancel={onCancel} />
      </Box>
    </PageContentWrapper>
  </>
);

export default CreateBIExport;

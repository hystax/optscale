import React from "react";
import { Box, Link } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import BIExportForm from "components/BIExportForm";
import { FIELD_NAMES } from "components/BIExportForm/FormElements";
import PageContentWrapper from "components/PageContentWrapper";
import { BI_EXPORTS, INTEGRATIONS } from "urls";
import { BI_EXPORT_STORAGE_TYPE } from "utils/biExport";

const { STORAGE_TYPE_FIELD_NAME } = FIELD_NAMES;

const defaultValues = {
  [STORAGE_TYPE_FIELD_NAME]: BI_EXPORT_STORAGE_TYPE.AWS_RAW_EXPORT
};

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

CreateBIExport.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  isLoadingProps: PropTypes.object
};

export default CreateBIExport;

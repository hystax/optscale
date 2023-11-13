import { useMemo } from "react";
import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import BIExportForm from "components/BIExportForm";
import { FIELD_NAMES } from "components/BIExportForm/FormElements";
import PageContentWrapper from "components/PageContentWrapper";
import { BI_EXPORTS, INTEGRATIONS, getBIExportUrl } from "urls";
import { BI_EXPORT_STORAGE_TYPE } from "utils/biExport";

const {
  STORAGE_TYPE_FIELD_NAME,
  NAME_FIELD_NAME,
  EXPORTED_DAYS_FIELD_NAME,
  AWS_ACCESS_KEY_ID_FIELD_NAME,
  AWS_SECRET_ACCESS_KEY_FIELD_NAME,
  BUCKET_NAME_FIELD_NAME,
  S3_PATH_FIELD_NAME,
  CONNECTION_STRING_FIELD_NAME,
  CONTAINER_FIELD_NAME
} = FIELD_NAMES;

const EditBIExport = ({ biExport, onSubmit, onCancel, isLoadingProps }) => {
  const { id, name, days, type, meta: { access_key_id: accessKeyId, bucket, s3_prefix: s3Prefix, container } = {} } = biExport;

  const defaultValues = useMemo(
    () => ({
      [NAME_FIELD_NAME]: name,
      [EXPORTED_DAYS_FIELD_NAME]: days,
      [STORAGE_TYPE_FIELD_NAME]: type ?? BI_EXPORT_STORAGE_TYPE.AWS_RAW_EXPORT,
      ...(type === BI_EXPORT_STORAGE_TYPE.AWS_RAW_EXPORT
        ? {
            [AWS_ACCESS_KEY_ID_FIELD_NAME]: accessKeyId,
            [AWS_SECRET_ACCESS_KEY_FIELD_NAME]: "",
            [BUCKET_NAME_FIELD_NAME]: bucket,
            [S3_PATH_FIELD_NAME]: s3Prefix
          }
        : {}),
      ...(type === BI_EXPORT_STORAGE_TYPE.AZURE_RAW_EXPORT
        ? {
            [CONNECTION_STRING_FIELD_NAME]: "",
            [CONTAINER_FIELD_NAME]: container
          }
        : {})
    }),
    [accessKeyId, bucket, container, days, name, s3Prefix, type]
  );

  return (
    <>
      <ActionBar
        data={{
          breadcrumbs: [
            <Link key={1} to={INTEGRATIONS} component={RouterLink}>
              <FormattedMessage id="integrations" />
            </Link>,
            <Link key={2} to={BI_EXPORTS} component={RouterLink}>
              <FormattedMessage id="biExportTitle" />
            </Link>,
            <Link key={3} to={getBIExportUrl(id)} component={RouterLink}>
              {name}
            </Link>
          ],
          title: {
            messageId: "editBIExportTitle",
            dataTestId: "lbl_edit_bi_export_title"
          }
        }}
      />
      <PageContentWrapper>
        <Box
          sx={{
            width: { md: "50%" }
          }}
        >
          <BIExportForm
            defaultValues={defaultValues}
            isLoadingProps={isLoadingProps}
            onSubmit={onSubmit}
            onCancel={onCancel}
            isEdit
          />
        </Box>
      </PageContentWrapper>
    </>
  );
};

export default EditBIExport;

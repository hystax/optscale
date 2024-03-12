import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import { BI_EXPORT_STORAGE_TYPE } from "utils/biExport";
import { AWS_CNR, AZURE_CNR } from "utils/constants";

const biExportTargetStorage = () => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_target_storage">
      <FormattedMessage id="targetStorage" />
    </TextWithDataTestId>
  ),
  id: "targetStorage",
  enableSorting: false,
  cell: ({
    row: {
      original: { meta, type }
    }
  }) => (
    <>
      {type === BI_EXPORT_STORAGE_TYPE.AWS_RAW_EXPORT && (
        <>
          <KeyValueLabel
            keyMessageId="type"
            value={<CloudLabel type={AWS_CNR} label={<FormattedMessage id="amazonS3" />} />}
            dataTestIds={{
              key: `p_amazon_S3_id`,
              value: `p_amazon_S3_value`
            }}
          />
          <KeyValueLabel
            keyMessageId="bucket"
            value={meta.bucket}
            dataTestIds={{
              key: `p_bucket_id`,
              value: `p_bucket_value`
            }}
          />
          <KeyValueLabel
            keyMessageId="s3Prefix"
            value={meta.s3_prefix}
            dataTestIds={{
              key: `p_s3_path_id`,
              value: `p_s3_path_value`
            }}
          />
        </>
      )}
      {type === BI_EXPORT_STORAGE_TYPE.AZURE_RAW_EXPORT && (
        <>
          <KeyValueLabel
            keyMessageId="type"
            value={<CloudLabel type={AZURE_CNR} label={<FormattedMessage id="azureBlobStorage" />} />}
            dataTestIds={{
              key: `p_azure_blob_storage_id`,
              value: `p_azure_blob_storage_value`
            }}
          />
          <KeyValueLabel
            keyMessageId="container"
            value={meta.container}
            dataTestIds={{
              key: `p_container_id`,
              value: `p_container_value`
            }}
          />
          <KeyValueLabel
            keyMessageId="storageAccount"
            value={meta.storage_account}
            dataTestIds={{
              key: `p_storage_account_id`,
              value: `p_storage_account_value`
            }}
          />
        </>
      )}
    </>
  )
});

export default biExportTargetStorage;

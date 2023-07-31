import React from "react";
import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import KeyValueLabelsList from "components/KeyValueLabelsList";
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
  }) => {
    const getItems = () => {
      if (type === BI_EXPORT_STORAGE_TYPE.AWS_RAW_EXPORT) {
        const { bucket, s3_prefix: s3Prefix } = meta;

        return [
          {
            itemKey: "type",
            messageId: "type",
            value: <CloudLabel type={AWS_CNR} label={<FormattedMessage id="amazonS3" />} />,
            dataTestIds: {
              key: `p_amazon_S3_id`,
              value: `p_amazon_S3_value`
            }
          },
          {
            itemKey: "bucket",
            messageId: "bucket",
            value: bucket,
            dataTestIds: {
              key: `p_bucket_id`,
              value: `p_bucket_value`
            }
          },
          {
            itemKey: "s3Prefix",
            messageId: "s3Prefix",
            value: s3Prefix,
            dataTestIds: {
              key: `p_s3_path_id`,
              value: `p_s3_path_value`
            }
          }
        ];
      }
      if (type === BI_EXPORT_STORAGE_TYPE.AZURE_RAW_EXPORT) {
        const { container, storage_account: storageAccount } = meta;

        return [
          {
            itemKey: "type",
            messageId: "type",
            value: <CloudLabel type={AZURE_CNR} label={<FormattedMessage id="azureBlobStorage" />} />,
            dataTestIds: {
              key: `p_azure_blob_storage_id`,
              value: `p_azure_blob_storage_value`
            }
          },
          {
            itemKey: "container",
            messageId: "container",
            value: container,
            dataTestIds: {
              key: `p_container_id`,
              value: `p_container_value`
            }
          },
          {
            itemKey: "storageAccount",
            messageId: "storageAccount",
            value: storageAccount,
            dataTestIds: {
              key: `p_storage_account_id`,
              value: `p_storage_account_value`
            }
          }
        ];
      }
      return [];
    };

    return <KeyValueLabelsList items={getItems()} />;
  }
});

export default biExportTargetStorage;

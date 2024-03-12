import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import SummaryList from "components/SummaryList";
import { BI_EXPORT_STORAGE_TYPE } from "utils/biExport";
import { AWS_CNR, AZURE_CNR } from "utils/constants";

const TypeLabel = ({ type }) => {
  const getValue = () =>
    ({
      [BI_EXPORT_STORAGE_TYPE.AWS_RAW_EXPORT]: <CloudLabel type={AWS_CNR} label={<FormattedMessage id="amazonS3" />} />,
      [BI_EXPORT_STORAGE_TYPE.AZURE_RAW_EXPORT]: (
        <CloudLabel type={AZURE_CNR} label={<FormattedMessage id="azureBlobStorage" />} />
      )
    })[type];

  return <KeyValueLabel key="type" keyMessageId="type" value={getValue()} />;
};

const TargetStorageSummaryList = ({ type, meta, isLoading = false }) => (
  <SummaryList
    titleMessage={<FormattedMessage id="targetStorage" />}
    isLoading={isLoading}
    items={[
      type && <TypeLabel key="type" type={type} />,
      ...(type === BI_EXPORT_STORAGE_TYPE.AWS_RAW_EXPORT
        ? [
            <KeyValueLabel key="bucket" keyMessageId="bucket" value={meta.bucket} />,
            <KeyValueLabel key="s3Prefix" keyMessageId="s3Prefix" value={meta.s3_prefix} />
          ]
        : []),
      ...(type === BI_EXPORT_STORAGE_TYPE.AZURE_RAW_EXPORT
        ? [
            <KeyValueLabel key="container" keyMessageId="container" value={meta.container} />,
            <KeyValueLabel key="storageAccount" keyMessageId="storageAccount" value={meta.storage_account} />
          ]
        : [])
    ]}
  />
);

export default TargetStorageSummaryList;

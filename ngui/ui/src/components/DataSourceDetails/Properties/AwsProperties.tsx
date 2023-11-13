import { FormattedMessage } from "react-intl";
import KeyValueLabelsList from "components/KeyValueLabelsList";
import { AWS_CNR } from "utils/constants";

const AwsProperties = ({ accountId, config }) => {
  const {
    access_key_id: accessKeyId,
    bucket_name: bucketName,
    bucket_prefix: buckerPrefix,
    linked,
    report_name: reportName
  } = config;

  const items = [
    {
      itemKey: "AWSAccountId",
      messageId: "AWSAccountId",
      value: accountId,
      dataTestIds: {
        key: `p_${AWS_CNR}_id`,
        value: `p_${AWS_CNR}_value`
      }
    },
    {
      itemKey: "awsAccountType",
      messageId: "awsAccountType",
      value: <FormattedMessage id={linked ? "linked" : "root"} />,
      dataTestIds: {
        key: `p_account_type_key`,
        value: `p_account_type_value`
      }
    },
    {
      itemKey: "awsAccessKeyId",
      messageId: "awsAccessKeyId",
      value: accessKeyId,
      dataTestIds: { key: "p_access_key_key", value: "p_access_key_value" }
    },
    {
      itemKey: "reportName",
      messageId: "reportName",
      value: reportName,
      dataTestIds: { key: "p_report_name_key", value: "p_report_name_value" }
    },
    {
      itemKey: "reportS3BucketName",
      messageId: "reportS3BucketName",
      value: bucketName,
      dataTestIds: { key: "p_bucket_name_key", value: "p_bucket_name_value" }
    },
    {
      itemKey: "reportPathPrefix",
      messageId: "reportPathPrefix",
      value: buckerPrefix,
      dataTestIds: { key: "p_bucket_prefix_key", value: "p_bucket_prefix_value" }
    }
  ];

  return <KeyValueLabelsList items={items} />;
};

export default AwsProperties;

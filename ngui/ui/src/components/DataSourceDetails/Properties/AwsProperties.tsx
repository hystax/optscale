import { FormattedMessage } from "react-intl";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { AWS_CNR } from "utils/constants";

const AwsProperties = ({ accountId, config }) => {
  const {
    access_key_id: accessKeyId,
    bucket_name: bucketName,
    bucket_prefix: buckerPrefix,
    linked,
    report_name: reportName
  } = config;

  return (
    <>
      <KeyValueLabel
        keyMessageId="AWSAccountId"
        value={accountId}
        dataTestIds={{
          key: `p_${AWS_CNR}_id`,
          value: `p_${AWS_CNR}_value`
        }}
      />
      <KeyValueLabel
        keyMessageId="awsAccountType"
        value={<FormattedMessage id={linked ? "linked" : "root"} />}
        dataTestIds={{
          key: `p_${AWS_CNR}_key`,
          value: `p_${AWS_CNR}_value`
        }}
      />
      <KeyValueLabel
        keyMessageId="awsAccessKeyId"
        value={accessKeyId}
        dataTestIds={{ key: "p_access_key_key", value: "p_access_key_value" }}
      />
      <KeyValueLabel
        keyMessageId="reportName"
        value={reportName}
        dataTestIds={{ key: "p_report_name_key", value: "p_report_name_value" }}
      />
      <KeyValueLabel
        keyMessageId="reportS3BucketName"
        value={bucketName}
        dataTestIds={{ key: "p_bucket_name_key", value: "p_bucket_name_value" }}
      />
      <KeyValueLabel
        keyMessageId="reportPathPrefix"
        value={buckerPrefix}
        dataTestIds={{ key: "p_bucket_prefix_key", value: "p_bucket_prefix_value" }}
      />
    </>
  );
};

export default AwsProperties;

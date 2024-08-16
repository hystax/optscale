import { FormattedMessage } from "react-intl";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { AWS_CNR, AWS_ROOT_CONNECT_CUR_VERSION, AWS_ROOT_CONNECT_CUR_VERSION_MESSAGE_ID } from "utils/constants";

type AwsPropertiesProps = {
  accountId: string;
  config: {
    access_key_id: string;
    bucket_name: string;
    bucket_prefix: string;
    linked: boolean;
    report_name: string;
    cur_version?: 1 | 2;
  };
};

const AwsProperties = ({ accountId, config }: AwsPropertiesProps) => {
  const {
    access_key_id: accessKeyId,
    bucket_name: bucketName,
    bucket_prefix: buckerPrefix,
    linked,
    cur_version: curVersion,
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
      {curVersion && Object.values(AWS_ROOT_CONNECT_CUR_VERSION).includes(curVersion) ? (
        <KeyValueLabel
          keyMessageId="exportType"
          value={<FormattedMessage id={AWS_ROOT_CONNECT_CUR_VERSION_MESSAGE_ID[curVersion]} />}
          dataTestIds={{ key: "p_cur_version_key", value: "p_cur_version_value" }}
        />
      ) : null}
      <KeyValueLabel
        keyMessageId="exportName"
        value={reportName}
        dataTestIds={{ key: "p_report_name_key", value: "p_report_name_value" }}
      />
      <KeyValueLabel
        keyMessageId="exportS3BucketName"
        value={bucketName}
        dataTestIds={{ key: "p_bucket_name_key", value: "p_bucket_name_value" }}
      />
      <KeyValueLabel
        keyMessageId="exportPathPrefix"
        value={buckerPrefix}
        dataTestIds={{ key: "p_bucket_prefix_key", value: "p_bucket_prefix_value" }}
      />
    </>
  );
};

export default AwsProperties;

import KeyValueLabelsList from "components/KeyValueLabelsList";

const NebiusProperties = ({ accountId, config }) => {
  const {
    cloud_name: cloudName,
    service_account_id: serviceAccountId,
    key_id: authorizedKeyId,
    access_key_id: accessKeyId,
    bucket_name: reportBucketName,
    bucket_prefix: reportPathPrefix
  } = config;

  const items = [
    {
      itemKey: "cloudId",
      messageId: "cloudId",
      value: accountId,
      dataTestIds: {
        key: `p_key_cloud_id`,
        value: `p_value_cloud_id`
      }
    },
    {
      itemKey: "cloudName",
      messageId: "cloudName",
      value: cloudName,
      dataTestIds: {
        key: `p_key_cloud_name`,
        value: `p_value_cloud_name`
      }
    },
    {
      itemKey: "serviceAccountId",
      messageId: "serviceAccountId",
      value: serviceAccountId,
      dataTestIds: {
        key: `p_key_service_account_id`,
        value: `p_value_service_account_id`
      }
    },
    {
      itemKey: "authorizedKeyId",
      messageId: "authorizedKeyId",
      value: authorizedKeyId,
      dataTestIds: {
        key: `p_key_authorized_key_id`,
        value: `p_value_authorized_key_id`
      }
    },
    {
      itemKey: "accessKeyId",
      messageId: "accessKeyId",
      value: accessKeyId,
      dataTestIds: {
        key: `p_key_authorized_key_id`,
        value: `p_value_authorized_key_id`
      }
    },
    {
      itemKey: "reportBucketName",
      messageId: "reportBucketName",
      value: reportBucketName,
      dataTestIds: {
        key: `p_key_bucket_name`,
        value: `p_value_bucket_name`
      }
    },
    {
      itemKey: "reportPathPrefix",
      messageId: "reportPathPrefix",
      value: reportPathPrefix,
      dataTestIds: {
        key: `p_key_bucket_prefix`,
        value: `p_value_bucket_prefix`
      }
    }
  ];

  return <KeyValueLabelsList items={items} />;
};

export default NebiusProperties;

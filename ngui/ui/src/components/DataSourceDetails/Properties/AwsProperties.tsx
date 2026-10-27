import { ReactNode } from "react";
import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import CopyText from "components/CopyText";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { useAllDataSources } from "hooks/coreData/useAllDataSources";
import { isEmptyArray } from "utils/arrays";
import { AWS_CNR, AWS_ROOT_CONNECT_CUR_VERSION, AWS_ROOT_CONNECT_CUR_VERSION_MESSAGE_ID } from "utils/constants";
import { AwsPropertiesProps } from "./types";

const LastImportFromRootAccount = ({
  cloudAccountId,
  awsAccountId,
}: {
  cloudAccountId?: string | null;
  awsAccountId?: string | null;
}) => {
  const dataSources = useAllDataSources();
  const rootDataSource = cloudAccountId ? dataSources.find((dataSource) => dataSource?.id === cloudAccountId) : undefined;

  const rootAccountKeyValueLabel = (value: ReactNode) => (
    <KeyValueLabel
      keyMessageId="lastFilledByRootAccount"
      value={value}
      dataTestIds={{ key: "p_last_import_from_key", value: "p_last_import_from_value" }}
    />
  );

  const rootAccountIdKeyValueLabel = () =>
    awsAccountId ? (
      <KeyValueLabel
        keyMessageId="rootAccountId"
        value={
          <CopyText sx={{ fontWeight: "inherit" }} text={awsAccountId}>
            {awsAccountId}
          </CopyText>
        }
        dataTestIds={{ key: "p_last_import_from_aws_id_key", value: "p_last_import_from_aws_id_value" }}
      />
    ) : null;

  // Root is still connected — link to it, plus its AWS account ID as its own copyable property.
  if (rootDataSource) {
    return (
      <>
        {rootAccountKeyValueLabel(<CloudLabel id={rootDataSource.id} name={rootDataSource.name} type={rootDataSource.type} />)}
        {rootAccountIdKeyValueLabel()}
      </>
    );
  }

  // Root was deleted (or its AWS account ID wasn't captured) — show whichever recorded ID we have as text, no link.
  if (cloudAccountId || awsAccountId) {
    const fallbackId = awsAccountId ?? cloudAccountId ?? "";
    return (
      <>
        {rootAccountKeyValueLabel(
          <>
            <CopyText sx={{ fontWeight: "inherit" }} text={fallbackId}>
              {fallbackId}
            </CopyText>{" "}
            <FormattedMessage id="deletedLabel" />
          </>
        )}
        {rootAccountIdKeyValueLabel()}
      </>
    );
  }

  // Never imported from a root.
  return rootAccountKeyValueLabel(<FormattedMessage id="unknown" />);
};

const AwsProperties = ({ accountId, config, createdAt, lastImportSourceId, lastImportSourceAccountId }: AwsPropertiesProps) => {
  const {
    access_key_id: accessKeyId,
    assume_role_account_id: assumeRoleAccountId,
    assume_role_name: assumeRoleName,
    assume_role_external_id: assumeRoleExternalId,
    bucket_name: bucketName,
    bucket_prefix: bucketPrefix,
    linked,
    cur_version: curVersion,
    report_name: reportName,
    use_edp_discount: useEdpDiscount,
    region_name: regionName,
    included_regions: includedRegions,
    excluded_regions: excludedRegions,
  } = config;

  const isAssumeRole = Boolean(assumeRoleAccountId && assumeRoleName);

  const getAwsAccountTypeMessageId = () => {
    if (linked) {
      return "member";
    }

    return "managementStandalone";
  };

  const getAwsAuthenticationTypeMessageId = () => {
    if (isAssumeRole) {
      return "assumedRole";
    }

    return "accessKey";
  };

  return (
    <>
      <KeyValueLabel
        keyMessageId="connectedAt"
        value={createdAt}
        dataTestIds={{
          key: `p_connected_at_id`,
          value: `p_connected_at_value`,
        }}
      />
      <KeyValueLabel
        keyMessageId="AWSAccountId"
        value={accountId}
        dataTestIds={{
          key: `p_${AWS_CNR}_id`,
          value: `p_${AWS_CNR}_value`,
        }}
      />
      <KeyValueLabel
        keyMessageId="awsAccountType"
        value={<FormattedMessage id={getAwsAccountTypeMessageId()} />}
        dataTestIds={{
          key: `p_${AWS_CNR}_key`,
          value: `p_${AWS_CNR}_value`,
        }}
      />
      <KeyValueLabel
        keyMessageId="awsAuthenticationType"
        value={<FormattedMessage id={getAwsAuthenticationTypeMessageId()} />}
        dataTestIds={{ key: "p_authentication_type_key", value: "p_authentication_type_value" }}
      />
      {isAssumeRole && (
        <>
          <KeyValueLabel
            keyMessageId="awsRoleName"
            value={assumeRoleName}
            dataTestIds={{ key: "p_assume_role_name_key", value: "p_assume_role_name_value" }}
          />
          {!!assumeRoleExternalId && (
            <KeyValueLabel
              keyMessageId="awsRoleExternalId"
              value={assumeRoleExternalId}
              dataTestIds={{ key: "p_assume_role_external_id_key", value: "p_assume_role_external_id_value" }}
            />
          )}
        </>
      )}
      {!isAssumeRole && (
        <KeyValueLabel
          keyMessageId="awsAccessKeyId"
          value={accessKeyId}
          dataTestIds={{ key: "p_access_key_key", value: "p_access_key_value" }}
        />
      )}
      {curVersion && Object.values(AWS_ROOT_CONNECT_CUR_VERSION).includes(curVersion) ? (
        <KeyValueLabel
          keyMessageId="exportType"
          value={<FormattedMessage id={AWS_ROOT_CONNECT_CUR_VERSION_MESSAGE_ID[curVersion]} />}
          dataTestIds={{ key: "p_cur_version_key", value: "p_cur_version_value" }}
        />
      ) : null}
      {!linked && (
        <>
          <KeyValueLabel
            keyMessageId="useAwsEdpDiscount"
            value={<FormattedMessage id={useEdpDiscount ? "yes" : "no"} />}
            dataTestIds={{ key: "p_use_edp_discount_key", value: "p_use_edp_discount_value" }}
          />
          <KeyValueLabel
            keyMessageId="exportName"
            value={reportName}
            dataTestIds={{ key: "p_export_name_key", value: "p_export_name_value" }}
          />
          <KeyValueLabel
            keyMessageId="exportS3BucketName"
            value={bucketName}
            dataTestIds={{ key: "p_bucket_name_key", value: "p_bucket_name_value" }}
          />
          <KeyValueLabel
            keyMessageId="exportPathPrefix"
            value={bucketPrefix}
            dataTestIds={{ key: "p_bucket_prefix_key", value: "p_bucket_prefix_value" }}
          />
          {!!regionName && (
            <KeyValueLabel
              keyMessageId="exportRegionName"
              value={regionName}
              dataTestIds={{ key: "p_region_name_key", value: "p_region_name_value" }}
            />
          )}
        </>
      )}
      {!isEmptyArray(includedRegions) && (
        <KeyValueLabel
          keyMessageId="regionScopeInclude"
          value={includedRegions?.join(", ")}
          dataTestIds={{ key: "p_included_regions_key", value: "p_included_regions_value" }}
        />
      )}
      {!isEmptyArray(excludedRegions) && (
        <KeyValueLabel
          keyMessageId="regionScopeExclude"
          value={excludedRegions?.join(", ")}
          dataTestIds={{ key: "p_excluded_regions_key", value: "p_excluded_regions_value" }}
        />
      )}
      {linked && <LastImportFromRootAccount cloudAccountId={lastImportSourceId} awsAccountId={lastImportSourceAccountId} />}
    </>
  );
};

export default AwsProperties;

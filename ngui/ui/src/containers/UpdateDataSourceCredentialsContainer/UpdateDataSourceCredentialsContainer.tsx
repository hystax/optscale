import { GET_AVAILABLE_FILTERS } from "api/restapi/actionTypes";
import UpdateDataSourceCredentialsForm from "components/forms/UpdateDataSourceCredentialsForm";
import { useUpdateDataSourceMutation } from "graphql/__generated__/hooks/restapi";
import { useRefetchApis } from "hooks/useRefetchApis";
import {
  ALIBABA_CNR,
  AWS_CNR,
  AZURE_CNR,
  AZURE_TENANT,
  DATABRICKS,
  GCP_CNR,
  GCP_TENANT,
  KUBERNETES_CNR,
  NEBIUS
} from "utils/constants";
import type { Config, Params, UpdateDataSourceCredentialsContainerProps } from "./types";

const UpdateDataSourceCredentialsContainer = ({
  id,
  type,
  config,
  closeSideModal
}: UpdateDataSourceCredentialsContainerProps) => {
  const refetch = useRefetchApis();

  const [updateDataSource, { loading }] = useUpdateDataSourceMutation();

  const getAwsConfigName = (config: Config) => {
    if (config.linked) {
      return "awsLinkedConfig";
    }

    if (config.assume_role_account_id && config.assume_role_name) {
      return "awsAssumedRoleConfig";
    }

    return "awsRootConfig";
  };

  const onSubmit = (dataSourceId: string, { config: newConfig }: Params) => {
    const configName = {
      [AWS_CNR]: getAwsConfigName(newConfig),
      [AZURE_TENANT]: "azureTenantConfig",
      [AZURE_CNR]: "azureSubscriptionConfig",
      [GCP_CNR]: "gcpConfig",
      [GCP_TENANT]: "gcpTenantConfig",
      [ALIBABA_CNR]: "alibabaConfig",
      [NEBIUS]: "nebiusConfig",
      [DATABRICKS]: "databricksConfig",
      [KUBERNETES_CNR]: "k8sConfig"
    }[type];

    updateDataSource({
      variables: {
        dataSourceId,
        params: {
          [configName]: newConfig
        }
      }
    }).then(() => {
      refetch([GET_AVAILABLE_FILTERS]);
      closeSideModal();
    });
  };

  return (
    <UpdateDataSourceCredentialsForm
      id={id}
      type={type}
      config={config}
      onSubmit={onSubmit}
      onCancel={closeSideModal}
      isLoading={loading}
    />
  );
};

export default UpdateDataSourceCredentialsContainer;

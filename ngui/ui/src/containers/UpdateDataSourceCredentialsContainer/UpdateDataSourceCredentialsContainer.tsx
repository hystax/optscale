import { useMutation } from "@apollo/client";
import UpdateDataSourceCredentialsForm from "components/forms/UpdateDataSourceCredentialsForm";
import { GET_DATA_SOURCE, UPDATE_DATA_SOURCE } from "graphql/api/rest/rest.queries";
import { ALIBABA_CNR, AWS_CNR, AZURE_CNR, AZURE_TENANT, DATABRICKS, GCP_CNR, KUBERNETES_CNR, NEBIUS } from "utils/constants";

const UpdateDataSourceCredentialsContainer = ({ id, type, config, closeSideModal }) => {
  const [updateDataSource, { loading }] = useMutation(UPDATE_DATA_SOURCE);

  const onSubmit = (dataSourceId, { config: newConfig }) => {
    const configName = {
      [AWS_CNR]: newConfig.linked ? "awsLinkedConfig" : "awsRootConfig",
      [AZURE_TENANT]: "azureTenantConfig",
      [AZURE_CNR]: "azureSubscriptionConfig",
      [GCP_CNR]: "gcpConfig",
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
      },
      refetchQueries: [GET_DATA_SOURCE]
    }).then(() => closeSideModal());
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

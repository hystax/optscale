import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import CloudLabel from "components/CloudLabel";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { useApiData } from "hooks/useApiData";
import { AZURE_CNR } from "utils/constants";

const AzureProperties = ({ config, parentId }) => {
  const { client_id: clientId, tenant, expense_import_scheme: expenseImportScheme, subscription_id: subscriptionId } = config;

  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_DATA_SOURCES);

  const { name, type } = cloudAccounts.find((cloudAccount) => cloudAccount.id === parentId) ?? {};

  return (
    <>
      {parentId && (
        <KeyValueLabel
          keyMessageId="parentDataSource"
          value={<CloudLabel id={parentId} name={name} type={type} />}
          dataTestIds={{ key: "p_parent_data_source_key", value: "p_parent_data_source_value" }}
        />
      )}
      {subscriptionId && (
        <KeyValueLabel
          keyMessageId="subscriptionId"
          value={subscriptionId}
          dataTestIds={{
            key: `p_${AZURE_CNR}_id`,
            value: `p_${AZURE_CNR}_value`
          }}
        />
      )}
      <KeyValueLabel
        keyMessageId="applicationClientId"
        value={clientId}
        dataTestIds={{ key: "p_client_id_key", value: "p_client_id_value" }}
      />
      <KeyValueLabel
        keyMessageId="directoryTenantId"
        value={tenant}
        dataTestIds={{ key: "p_tenant_key", value: "p_tenant_value" }}
      />
      <KeyValueLabel
        keyMessageId="expenseImportScheme"
        value={expenseImportScheme}
        dataTestIds={{ key: "p_expense_import_scheme_key", value: "p_expense_import_scheme_value" }}
      />
    </>
  );
};

export default AzureProperties;

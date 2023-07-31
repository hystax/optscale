import React from "react";
import PropTypes from "prop-types";
import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import CloudLabel from "components/CloudLabel";
import KeyValueLabelsList from "components/KeyValueLabelsList";
import { useApiData } from "hooks/useApiData";
import { AZURE_CNR } from "utils/constants";

const AzureProperties = ({ config, parentId }) => {
  const { client_id: clientId, tenant, expense_import_scheme: expenseImportScheme, subscription_id: subscriptionId } = config;

  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_DATA_SOURCES);

  const { name, type } = cloudAccounts.find((cloudAccount) => cloudAccount.id === parentId) ?? {};

  const items = [
    parentId && {
      itemKey: "parentDataSource",
      messageId: "parentDataSource",
      value: <CloudLabel id={parentId} name={name} type={type} />,
      dataTestIds: { key: "p_parent_data_source_key", value: "p_parent_data_source_value" }
    },
    subscriptionId && {
      itemKey: "subscriptionId",
      messageId: "subscriptionId",
      value: subscriptionId,
      dataTestIds: {
        key: `p_${AZURE_CNR}_id`,
        value: `p_${AZURE_CNR}_value`
      }
    },
    {
      itemKey: "applicationClientId",
      messageId: "applicationClientId",
      value: clientId,
      dataTestIds: { key: "p_client_id_key", value: "p_client_id_value" }
    },
    {
      itemKey: "directoryTenantId",
      messageId: "directoryTenantId",
      value: tenant,
      dataTestIds: { key: "p_tenant_key", value: "p_tenant_value" }
    },
    {
      itemKey: "expenseImportScheme",
      messageId: "expenseImportScheme",
      value: expenseImportScheme,
      dataTestIds: { key: "p_expense_import_scheme_key", value: "p_expense_import_scheme_value" }
    }
  ].filter(Boolean);

  return <KeyValueLabelsList items={items} />;
};

AzureProperties.propTypes = {
  name: PropTypes.string,
  type: PropTypes.string,
  parentId: PropTypes.string,
  config: PropTypes.shape({
    client_id: PropTypes.string,
    subscription_id: PropTypes.string,
    tenant: PropTypes.string,
    expense_import_scheme: PropTypes.string
  })
};

export default AzureProperties;

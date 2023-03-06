import React from "react";
import PropTypes from "prop-types";
import KeyValueLabelsList from "components/KeyValueLabelsList";
import { AZURE_CNR } from "utils/constants";

const AzureProperties = ({ accountId, config }) => {
  const { client_id: clientId, tenant, expense_import_scheme: expenseImportScheme } = config;

  const items = [
    {
      itemKey: "subscriptionId",
      messageId: "subscriptionId",
      value: accountId,
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
  ];

  return <KeyValueLabelsList items={items} />;
};

AzureProperties.propTypes = {
  accountId: PropTypes.string.isRequired,
  config: PropTypes.shape({
    client_id: PropTypes.string,
    subscription_id: PropTypes.string,
    tenant: PropTypes.string,
    expense_import_scheme: PropTypes.string
  })
};

export default AzureProperties;

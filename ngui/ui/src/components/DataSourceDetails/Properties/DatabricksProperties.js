import React from "react";
import PropTypes from "prop-types";
import KeyValueLabelsList from "components/KeyValueLabelsList";
import { DATABRICKS } from "utils/constants";

const DatabricksProperties = ({ accountId, config }) => {
  const { client_id: clientId } = config;

  const items = [
    {
      itemKey: "accountId",
      messageId: "accountId",
      value: accountId,
      dataTestIds: {
        key: `p_${DATABRICKS}_id`,
        value: `p_${DATABRICKS}_value`
      }
    },
    {
      itemKey: "clientId",
      messageId: "clientId",
      value: clientId,
      dataTestIds: {
        key: "p_client_id_key",
        value: "p_client_id_value"
      }
    }
  ];

  return <KeyValueLabelsList items={items} />;
};

DatabricksProperties.propTypes = {
  accountId: PropTypes.string.isRequired,
  config: PropTypes.object.isRequired
};

export default DatabricksProperties;

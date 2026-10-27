import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { DATABRICKS } from "utils/constants";
import { DatabricksPropertiesProps } from "./types";

const DatabricksProperties = ({ accountId, config, createdAt }: DatabricksPropertiesProps) => {
  const { client_id: clientId } = config;

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
        keyMessageId="accountId"
        value={accountId}
        dataTestIds={{
          key: `p_${DATABRICKS}_id`,
          value: `p_${DATABRICKS}_value`,
        }}
      />
      <KeyValueLabel
        keyMessageId="clientId"
        value={clientId}
        dataTestIds={{
          key: "p_client_id_key",
          value: "p_client_id_value",
        }}
      />
    </>
  );
};

export default DatabricksProperties;

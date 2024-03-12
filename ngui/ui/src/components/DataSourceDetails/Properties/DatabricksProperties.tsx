import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { DATABRICKS } from "utils/constants";

const DatabricksProperties = ({ accountId, config }) => {
  const { client_id: clientId } = config;

  return (
    <>
      <KeyValueLabel
        keyMessageId="accountId"
        value={accountId}
        dataTestIds={{
          key: `p_${DATABRICKS}_id`,
          value: `p_${DATABRICKS}_value`
        }}
      />
      <KeyValueLabel
        keyMessageId="clientId"
        value={clientId}
        dataTestIds={{
          key: "p_client_id_key",
          value: "p_client_id_value"
        }}
      />
    </>
  );
};

export default DatabricksProperties;

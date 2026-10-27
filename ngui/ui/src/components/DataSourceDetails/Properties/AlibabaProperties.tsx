import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { ALIBABA_CNR } from "utils/constants";
import { AlibabaPropertiesProps } from "./types";

const AlibabaProperties = ({ accountId, config, createdAt }: AlibabaPropertiesProps) => {
  const { access_key_id: accessKeyId } = config;

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
        key="alibabaAccountId"
        keyMessageId="alibabaAccountId"
        value={accountId}
        dataTestIds={{
          key: `p_${ALIBABA_CNR}_id`,
          value: `p_${ALIBABA_CNR}_value`,
        }}
      />
      <KeyValueLabel
        key="alibabaAccessKeyId"
        keyMessageId="alibabaAccessKeyId"
        value={accessKeyId}
        dataTestIds={{ key: "p_access_key_key", value: "p_access_key_value" }}
      />
    </>
  );
};

export default AlibabaProperties;

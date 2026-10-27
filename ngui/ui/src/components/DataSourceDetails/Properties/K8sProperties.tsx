import { FormattedMessage } from "react-intl";
import CopyText from "components/CopyText";
import CostModelFormattedMoney from "components/CostModelFormattedMoney";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { KUBERNETES_CNR } from "utils/constants";
import { K8sPropertiesProps } from "./types";

const K8sProperties = ({ id, accountId, config, createdAt }: K8sPropertiesProps) => {
  const {
    cost_model: { cpu_hourly_cost: cpuHourlyCost, memory_hourly_cost: memoryHourlyCost } = {},
    user,
    custom_price: customPrice,
  } = config;

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
        keyMessageId="kubernetesId"
        value={accountId}
        dataTestIds={{
          key: `p_${KUBERNETES_CNR}_id`,
          value: `p_${KUBERNETES_CNR}_value`,
        }}
      />
      <KeyValueLabel
        keyMessageId="dataSourceId"
        value={
          <CopyText sx={{ fontWeight: "inherit" }} text={id}>
            {id}
          </CopyText>
        }
        dataTestIds={{ key: "p_data_source_id", value: "value_data_source_id" }}
      />
      <KeyValueLabel keyMessageId="user" value={user} dataTestIds={{ key: "p_user_key", value: "p_user_value" }} />
      <KeyValueLabel
        keyMessageId="costModel"
        value={<FormattedMessage id={customPrice ? "default" : "flavorBased"} />}
        dataTestIds={{ key: "p_cost_model_key", value: "p_cost_model_value" }}
      />
      {customPrice && (
        <>
          <KeyValueLabel
            keyMessageId="cpuPerHour"
            value={<CostModelFormattedMoney value={cpuHourlyCost} />}
            dataTestIds={{ key: "p_cpu_per_hour_key", value: "p_cpu_per_hour_value" }}
          />
          <KeyValueLabel
            keyMessageId="memoryPerHour"
            value={<CostModelFormattedMoney value={memoryHourlyCost} />}
            dataTestIds={{ key: "p_memory_per_hour_key", value: "p_memory_per_hour_value" }}
          />
        </>
      )}
    </>
  );
};

export default K8sProperties;

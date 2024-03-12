import CopyText from "components/CopyText";
import CostModelFormattedMoney from "components/CostModelFormattedMoney";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { KUBERNETES_CNR } from "utils/constants";

const K8sProperties = ({ id, accountId, config }) => {
  const { cost_model: { cpu_hourly_cost: cpuHourlyCost, memory_hourly_cost: memoryHourlyCost } = {}, user } = config;

  return (
    <>
      <KeyValueLabel
        keyMessageId="kubernetesId"
        value={accountId}
        dataTestIds={{
          key: `p_${KUBERNETES_CNR}_id`,
          value: `p_${KUBERNETES_CNR}_value`
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
  );
};

export default K8sProperties;

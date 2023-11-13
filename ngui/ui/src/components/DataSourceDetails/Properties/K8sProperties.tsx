import CopyText from "components/CopyText";
import CostModelFormattedMoney from "components/CostModelFormattedMoney";
import KeyValueLabelsList from "components/KeyValueLabelsList";
import { KUBERNETES_CNR } from "utils/constants";

const K8sProperties = ({ id, accountId, config }) => {
  const { cost_model: { cpu_hourly_cost: cpuHourlyCost, memory_hourly_cost: memoryHourlyCost } = {}, user } = config;

  const items = [
    {
      itemKey: "kubernetesId",
      messageId: "kubernetesId",
      value: accountId,
      dataTestIds: {
        key: `p_${KUBERNETES_CNR}_id`,
        value: `p_${KUBERNETES_CNR}_value`
      }
    },
    {
      itemKey: "dataSourceId",
      messageId: "dataSourceId",
      value: (
        <CopyText text={id}>
          <strong>{id}</strong>
        </CopyText>
      ),
      dataTestIds: { key: "p_data_source_id", value: "value_data_source_id" },
      isBoldValue: false
    },
    {
      itemKey: "user",
      messageId: "user",
      value: user,
      dataTestIds: { key: "p_user_key", value: "p_user_value" }
    },
    {
      itemKey: "cpuPerHour",
      messageId: "cpuPerHour",
      value: <CostModelFormattedMoney value={cpuHourlyCost} />,
      dataTestIds: { key: "p_cpu_per_hour_key", value: "p_cpu_per_hour_value" }
    },
    {
      itemKey: "memoryPerHour",
      messageId: "memoryPerHour",
      value: <CostModelFormattedMoney value={memoryHourlyCost} />,
      dataTestIds: { key: "p_memory_per_hour_key", value: "p_memory_per_hour_value" }
    }
  ];

  return <KeyValueLabelsList items={items} />;
};

export default K8sProperties;

import { UPDATE_DATA_SOURCE } from "api/restapi/actionTypes";
import CostModelForm from "components/forms/CostModelForm";
import { useApiState } from "hooks/useApiState";
import DataSourcesService from "services/DataSourcesService";

const CostModelFormContainer = ({ cloudAccountId, costModel = {}, onSuccess, onCancel }) => {
  const { isLoading } = useApiState(UPDATE_DATA_SOURCE);

  const { useUpdateDataSource } = DataSourcesService();

  const { onUpdate } = useUpdateDataSource();

  return (
    <CostModelForm
      onSubmit={(formData) =>
        onUpdate(cloudAccountId, {
          config: {
            cost_model: {
              cpu_hourly_cost: Number(formData.cpuPerHour),
              memory_hourly_cost: Number(formData.memoryPerHour)
            }
          }
        }).then(() => onSuccess())
      }
      onCancel={onCancel}
      cpuHour={costModel.cpu_hourly_cost}
      memoryMbHour={costModel.memory_hourly_cost}
      isLoading={isLoading}
    />
  );
};

export default CostModelFormContainer;

import React from "react";
import PropTypes from "prop-types";
import { UPDATE_CLOUD_ACCOUNT } from "api/restapi/actionTypes";
import CostModelForm from "components/CostModelForm";
import { useApiState } from "hooks/useApiState";
import DataSourcesService from "services/DataSourcesService";

const CostModelFormContainer = ({ cloudAccountId, costModel = {}, onSuccess, onCancel }) => {
  const { isLoading } = useApiState(UPDATE_CLOUD_ACCOUNT);

  const { useUpdateDataSource } = DataSourcesService();

  const { onUpdate } = useUpdateDataSource();

  const onSubmit = (formData) =>
    onUpdate(cloudAccountId, {
      config: {
        cost_model: {
          cpu_hourly_cost: formData.cpuHour,
          memory_hourly_cost: formData.memoryMbHour
        }
      }
    }).then(() => onSuccess());

  return (
    <CostModelForm
      onSubmit={onSubmit}
      onCancel={onCancel}
      cpuHour={costModel.cpu_hourly_cost}
      memoryMbHour={costModel.memory_hourly_cost}
      isLoading={isLoading}
    />
  );
};

CostModelFormContainer.propTypes = {
  cloudAccountId: PropTypes.string.isRequired,
  costModel: PropTypes.shape({
    cpu_hourly_cost: PropTypes.number,
    memory_hourly_cost: PropTypes.number
  }).isRequired,
  onSuccess: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired
};

export default CostModelFormContainer;

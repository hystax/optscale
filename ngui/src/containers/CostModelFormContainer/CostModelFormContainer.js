import React from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { updateCloudAccount } from "api";
import { UPDATE_CLOUD_ACCOUNT } from "api/restapi/actionTypes";
import CostModelForm from "components/CostModelForm";
import { useApiState } from "hooks/useApiState";

const CostModelFormContainer = ({ cloudAccountId, costModel = {} }) => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(UPDATE_CLOUD_ACCOUNT);

  const onSubmit = (formData) => dispatch(updateCloudAccount(cloudAccountId, formData));

  return (
    <CostModelForm
      onSubmit={onSubmit}
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
  }).isRequired
};

export default CostModelFormContainer;

import React from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { updateResourceCostModel } from "api/restapi";
import { UPDATE_RESOURCE_COST_MODEL } from "api/restapi/actionTypes";
import EnvironmentCostModelForm from "components/EnvironmentCostModelForm";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";

const EnvironmentCostModelFormContainer = ({ resourceId, hourlyPrice, onCancel }) => {
  const dispatch = useDispatch();

  const onSubmit = (formData) =>
    dispatch((_, getState) => {
      dispatch(updateResourceCostModel(resourceId, formData)).then(() => {
        if (!isError(UPDATE_RESOURCE_COST_MODEL, getState())) {
          onCancel();
        }
      });
    });

  const { isLoading } = useApiState(UPDATE_RESOURCE_COST_MODEL);

  return (
    <EnvironmentCostModelForm onSubmit={onSubmit} defaultHourlyPrice={hourlyPrice} isLoading={isLoading} onCancel={onCancel} />
  );
};

EnvironmentCostModelFormContainer.propTypes = {
  resourceId: PropTypes.string.isRequired,
  hourlyPrice: PropTypes.number,
  onCancel: PropTypes.func.isRequired
};

export default EnvironmentCostModelFormContainer;

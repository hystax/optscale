import { useDispatch } from "react-redux";
import { updateResourceCostModel } from "api/restapi";
import { UPDATE_RESOURCE_COST_MODEL } from "api/restapi/actionTypes";
import EnvironmentCostModelForm from "components/forms/EnvironmentCostModelForm";
import { FormValues } from "components/forms/EnvironmentCostModelForm/types";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";

const EnvironmentCostModelFormContainer = ({ resourceId, hourlyPrice, onCancel }) => {
  const dispatch = useDispatch();

  const onSubmit = (formData: FormValues) =>
    dispatch((_, getState) => {
      dispatch(
        updateResourceCostModel(resourceId, {
          hourlyPrice: Number(formData.hourlyPrice)
        })
      ).then(() => {
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

export default EnvironmentCostModelFormContainer;

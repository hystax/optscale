import { useDispatch } from "react-redux";
import { updateEnvironmentProperty } from "api";
import { UPDATE_ENVIRONMENT_PROPERTY } from "api/restapi/actionTypes";
import DeleteEntity from "components/DeleteEntity";
import { useApiState } from "hooks/useApiState";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import { checkError } from "utils/api";

const DeletePropertyContainer = ({ environmentId, propertyName, onSuccess, onCancel }) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const dispatch = useDispatch();

  const { isLoading } = useApiState(UPDATE_ENVIRONMENT_PROPERTY);

  const onSubmit = () => {
    dispatch((_, getState) => {
      dispatch(updateEnvironmentProperty(environmentId, { propertyName, propertyValue: null }))
        .then(() => checkError(UPDATE_ENVIRONMENT_PROPERTY, getState()))
        .then(() => typeof onSuccess === "function" && onSuccess());
    });
  };

  return (
    <DeleteEntity
      onDelete={onSubmit}
      onCancel={onCancel}
      isLoading={isLoading}
      deleteButtonProps={{
        onDelete: onSubmit,
        disabled: isRestricted,
        tooltip: {
          show: isRestricted,
          value: restrictionReasonMessage,
        },
      }}
      message={{
        messageId: "deleteEnvironmentPropertyQuestion",
      }}
    />
  );
};

export default DeletePropertyContainer;

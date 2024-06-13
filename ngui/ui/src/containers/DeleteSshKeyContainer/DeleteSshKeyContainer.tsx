import { useDispatch } from "react-redux";
import { deleteSshKey, updateSshKey } from "api";
import { DELETE_SSH_KEY, UPDATE_SSH_KEY } from "api/restapi/actionTypes";
import DeleteSshKeyForm from "components/forms/DeleteSshKeyForm";
import { FormValues } from "components/forms/DeleteSshKeyForm/types";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";

const DeleteSshKeyContainer = ({ keys, currentKeyId, closeSideModal, isDefault }) => {
  const dispatch = useDispatch();

  const { isLoading: isDeleteKeyLoading } = useApiState(DELETE_SSH_KEY);
  const { isLoading: isUpdateKeyLoading } = useApiState(UPDATE_SSH_KEY);

  const keysToSelect = keys.filter(({ id }) => id !== currentKeyId);

  const doRemove = () =>
    dispatch((_, getState) => {
      dispatch(deleteSshKey(currentKeyId)).then(() => {
        if (!isError(DELETE_SSH_KEY, getState())) {
          closeSideModal();
        }
      });
    });

  const onSubmit = (formData: FormValues) => {
    const { newDefaultKey } = formData;

    if (isDefault && newDefaultKey) {
      dispatch((_, getState) => {
        dispatch(updateSshKey(newDefaultKey, { default: true })).then(() => {
          if (!isError(UPDATE_SSH_KEY, getState())) {
            doRemove();
          }
        });
      });
    } else {
      doRemove();
    }
  };

  return (
    <DeleteSshKeyForm
      isLoading={isDeleteKeyLoading || isUpdateKeyLoading}
      onSubmit={onSubmit}
      keysToSelect={keysToSelect}
      isDefaultKey={isDefault}
      closeSideModal={closeSideModal}
    />
  );
};

export default DeleteSshKeyContainer;

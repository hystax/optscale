import React from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { deleteSshKey, updateSshKey } from "api";
import { DELETE_SSH_KEY, UPDATE_SSH_KEY } from "api/restapi/actionTypes";
import DeleteSshKeyForm, { NEW_DEFAULT_KEY } from "components/DeleteSshKeyForm";
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

  const onSubmit = (formData) => {
    const { [NEW_DEFAULT_KEY]: newKey } = formData;

    if (isDefault && newKey) {
      dispatch((_, getState) => {
        dispatch(updateSshKey(newKey, { default: true })).then(() => {
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

DeleteSshKeyContainer.propTypes = {
  keys: PropTypes.array,
  currentKeyId: PropTypes.string,
  isDefault: PropTypes.bool,
  closeSideModal: PropTypes.func.isRequired
};

export default DeleteSshKeyContainer;

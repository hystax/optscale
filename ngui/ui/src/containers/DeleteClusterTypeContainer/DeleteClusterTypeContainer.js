import React from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { deleteClusterType } from "api";
import { DELETE_CLUSTER_TYPE } from "api/restapi/actionTypes";
import DeleteEntity from "components/DeleteEntity";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";

const DeleteClusterTypeContainer = ({ onCancel, clusterTypeId, clusterTypeName }) => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(DELETE_CLUSTER_TYPE);

  const onSubmit = () => {
    dispatch((_, getState) => {
      dispatch(deleteClusterType(clusterTypeId))
        .then(() => {
          if (isError(DELETE_CLUSTER_TYPE, getState())) {
            return Promise.reject();
          }
          return Promise.resolve();
        })
        .then(onCancel);
    });
  };

  return (
    <DeleteEntity
      onDelete={onSubmit}
      onCancel={onCancel}
      isLoading={isLoading}
      deleteButtonProps={{
        onDelete: onSubmit
      }}
      dataTestIds={{
        text: "p_delete",
        deleteButton: "btn_smodal_delete",
        cancelButton: "btn_cancel"
      }}
      message={{
        messageId: "deleteClusterTypeQuestion",
        values: {
          clusterTypeName
        }
      }}
    />
  );
};

DeleteClusterTypeContainer.propTypes = {
  onCancel: PropTypes.func.isRequired,
  clusterTypeId: PropTypes.string.isRequired,
  clusterTypeName: PropTypes.string.isRequired
};

export default DeleteClusterTypeContainer;

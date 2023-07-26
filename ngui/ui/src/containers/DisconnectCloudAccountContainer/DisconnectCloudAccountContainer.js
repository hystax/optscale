import React from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { disconnectDataSource } from "api";
import { DELETE_DATA_SOURCE } from "api/restapi/actionTypes";
import DisconnectCloudAccount from "components/DisconnectCloudAccount";
import { useApiState } from "hooks/useApiState";
import { CLOUD_ACCOUNTS } from "urls";
import { isError } from "utils/api";

const DisconnectCloudAccountContainer = ({ id, type, parentId, onCancel }) => {
  const { isLoading } = useApiState(DELETE_DATA_SOURCE);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const onSubmit = (cloudAccountId) =>
    dispatch((_, getState) => {
      dispatch(disconnectDataSource(cloudAccountId)).then(() => {
        if (!isError(DELETE_DATA_SOURCE, getState())) {
          navigate(CLOUD_ACCOUNTS);
        }
      });
    });

  return (
    <DisconnectCloudAccount
      id={id}
      type={type}
      parentId={parentId}
      onCancel={onCancel}
      isLoading={isLoading}
      onSubmit={onSubmit}
    />
  );
};

DisconnectCloudAccountContainer.propTypes = {
  id: PropTypes.string.isRequired,
  onCancel: PropTypes.func.isRequired,
  type: PropTypes.string.isRequired,
  parentId: PropTypes.string
};

export default DisconnectCloudAccountContainer;

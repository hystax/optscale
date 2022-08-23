import React from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { disconnectCloudAccount } from "api";
import { DELETE_CLOUD_ACCOUNT } from "api/restapi/actionTypes";
import DisconnectCloudAccount from "components/DisconnectCloudAccount";
import { useApiState } from "hooks/useApiState";
import { CLOUD_ACCOUNTS } from "urls";
import { isError } from "utils/api";

const DisconnectCloudAccountContainer = ({ id, type, onCancel }) => {
  const { isLoading } = useApiState(DELETE_CLOUD_ACCOUNT);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const onSubmit = (cloudAccountId) =>
    dispatch((_, getState) => {
      dispatch(disconnectCloudAccount(cloudAccountId)).then(() => {
        if (!isError(DELETE_CLOUD_ACCOUNT, getState())) {
          navigate(CLOUD_ACCOUNTS);
        }
      });
    });

  return <DisconnectCloudAccount id={id} type={type} onCancel={onCancel} isLoading={isLoading} onSubmit={onSubmit} />;
};

DisconnectCloudAccountContainer.propTypes = {
  id: PropTypes.string.isRequired,
  onCancel: PropTypes.func.isRequired,
  type: PropTypes.string.isRequired
};

export default DisconnectCloudAccountContainer;

import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { updateUserAssignment } from "api";
import { UPDATE_USER_ASSIGNMENT } from "api/jira_bus/actionTypes";
import ConnectJira from "components/ConnectJira";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";

const ConnectJiraContainer = ({ secret }) => {
  const dispatch = useDispatch();
  const [hasError, setHasError] = useState(false);

  const { isLoading } = useApiState(UPDATE_USER_ASSIGNMENT);

  useEffect(() => {
    dispatch((_, getState) => {
      dispatch(updateUserAssignment(secret))
        .then(() => {
          if (isError(UPDATE_USER_ASSIGNMENT, getState())) {
            return Promise.reject();
          }
          return window.close();
        })
        .catch(() => setHasError(true));
    });
  }, [dispatch, secret]);

  return <ConnectJira isLoading={isLoading} isError={hasError} />;
};

ConnectJiraContainer.propTypes = {
  secret: PropTypes.string.isRequired
};

export default ConnectJiraContainer;

import React, { useState } from "react";
import PropTypes from "prop-types";
import LogoutFromOptscaleButton from "../../components/LogoutFromOptscaleButton";
import makeRequest from "../../utils/makeRequest";

const LogoutFromOptscaleButtonContainer = ({ onSuccess }) => {
  const [isLoading, setIsLoading] = useState(false);

  const onLogoutButtonClick = () => {
    setIsLoading(true);
    makeRequest({
      url: "/jira_bus/v2/user_assignment",
      options: { method: "DELETE" }
    })
      .then(() => {
        setIsLoading(false);
        onSuccess();
      })
      .catch(() => {
        setIsLoading(false);
      });
  };

  return <LogoutFromOptscaleButton isLoading={isLoading} onLogoutButtonClick={onLogoutButtonClick} />;
};

LogoutFromOptscaleButtonContainer.propTypes = {
  onSuccess: PropTypes.func.isRequired
};

export default LogoutFromOptscaleButtonContainer;

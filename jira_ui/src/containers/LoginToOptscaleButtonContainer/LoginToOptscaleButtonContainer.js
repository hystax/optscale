import React, { useRef, useState } from "react";
import PropTypes from "prop-types";
import LoginToOptscaleButton from "components/LoginToOptscaleButton";
import makeRequest from "utils/makeRequest";

const LoginToOptscaleButtonContainer = ({ onSuccess }) => {
  const [isLoading, setIsLoading] = useState(false);

  const windowRef = useRef({
    checkWindow: false,
    connectionWindow: null
  });

  const checkConnectionWindow = () => {
    if (windowRef.current.checkWindow) {
      if (windowRef.current.connectionWindow && windowRef.current.connectionWindow.closed) {
        onSuccess();
      } else {
        setTimeout(() => {
          checkConnectionWindow();
        }, 1000);
      }
    }
  };

  const openOptscaleJiraConnection = (connectionUrl) => {
    windowRef.current.connectionWindow = window.open(connectionUrl, "_blank");
    windowRef.current.checkWindow = true;

    // browsers can prevent opening a new tab depending on their settings
    if (windowRef.current.connectionWindow) {
      checkConnectionWindow();
    }
  };

  const onLoginButtonClick = () => {
    setIsLoading(true);

    makeRequest({
      url: "/jira_bus/v2/user_assignment",
      options: { method: "POST" }
    })
      .then(({ data, error }) => {
        setIsLoading(false);

        const secret = data?.secret;

        if (!error && secret) {
          openOptscaleJiraConnection(`/jira/connect/${secret}`);
        }
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

  return <LoginToOptscaleButton isLoading={isLoading} onLoginButtonClick={onLoginButtonClick} />;
};

LoginToOptscaleButtonContainer.propTypes = {
  onSuccess: PropTypes.func.isRequired
};

export default LoginToOptscaleButtonContainer;

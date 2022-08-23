import React from "react";
import PropTypes from "prop-types";
import LoginToOptscaleButtonContainer from "containers/LoginToOptscaleButtonContainer";
import LogoutFromOptscaleButtonContainer from "containers/LogoutFromOptscaleButtonContainer";

const ConnectToOptscaleSection = ({ onSuccessLogin, onSuccessLogout, isConnected }) => {
  const getConnectionContent = () => {
    const { message, button } = isConnected
      ? {
          message: "You have connected your Jira to OptScale.",
          button: <LogoutFromOptscaleButtonContainer onSuccess={onSuccessLogout} />
        }
      : {
          message: "Please log in to OptScale to connect this Jira instance to your organization.",
          button: <LoginToOptscaleButtonContainer onSuccess={onSuccessLogin} />
        };

    return (
      <div>
        <p style={{ marginBottom: "16px" }}>{message}</p>
        {button}
      </div>
    );
  };

  return (
    <div>
      <p style={{ fontWeight: "bold", marginBottom: "16px" }}>Connect OptScale Account</p>
      {getConnectionContent()}
    </div>
  );
};

ConnectToOptscaleSection.propTypes = {
  onSuccessLogin: PropTypes.func,
  onSuccessLogout: PropTypes.func,
  isConnected: PropTypes.bool
};

export default ConnectToOptscaleSection;

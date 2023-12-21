import React from "react";
import { LoadingButton } from "@atlaskit/button";
import PropTypes from "prop-types";

const LogoutFromOptscaleButton = ({ isLoading = false, onLogoutButtonClick }) => (
  <LoadingButton appearance="warning" isLoading={isLoading} onClick={onLogoutButtonClick}>
    Log out from OptScale
  </LoadingButton>
);

LogoutFromOptscaleButton.propTypes = {
  isLoading: PropTypes.bool,
  onLogoutButtonClick: PropTypes.func.isRequired
};

export default LogoutFromOptscaleButton;

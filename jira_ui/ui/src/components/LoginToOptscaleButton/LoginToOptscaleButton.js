import React from "react";
import { LoadingButton } from "@atlaskit/button";
import PropTypes from "prop-types";

const LoginToOptscaleButton = ({ onLoginButtonClick, isLoading }) => (
  <LoadingButton isLoading={isLoading} appearance="primary" onClick={onLoginButtonClick}>
    Log in to OptScale
  </LoadingButton>
);

LoginToOptscaleButton.propTypes = {
  onLoginButtonClick: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default LoginToOptscaleButton;

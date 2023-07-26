import React from "react";
import PropTypes from "prop-types";
import Greeter from "components/Greeter";
import ResetPasswordForm from "components/ResetPasswordForm";

const ResetPassword = ({ onSubmit, isLoading, sendState }) => (
  <Greeter form={<ResetPasswordForm onSubmit={onSubmit} isLoading={isLoading} sendState={sendState} />} />
);

ResetPassword.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
  sendState: PropTypes.string.isRequired
};

export default ResetPassword;

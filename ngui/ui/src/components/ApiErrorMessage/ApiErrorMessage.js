import React from "react";
import PropTypes from "prop-types";
import ApiMessage from "components/ApiMessage";

const ApiErrorMessage = ({ errorCode, reason, url, params = [] }) => (
  <ApiMessage defaultMessage={`${url}: ${reason}`} code={errorCode} params={params} />
);

ApiErrorMessage.propTypes = {
  errorCode: PropTypes.string.isRequired,
  reason: PropTypes.string.isRequired,
  url: PropTypes.string.isRequired,
  params: PropTypes.array
};

export default ApiErrorMessage;

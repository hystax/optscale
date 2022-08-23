import React from "react";
import PropTypes from "prop-types";
import ApiMessage from "components/ApiMessage";

const ApiSuccessMessage = ({ successCode, params }) => <ApiMessage code={successCode} params={params} />;

ApiSuccessMessage.propTypes = {
  successCode: PropTypes.string.isRequired,
  params: PropTypes.array
};

export default ApiSuccessMessage;

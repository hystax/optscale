import React from "react";
import PropTypes from "prop-types";
import ErrorComponent from "components/Error";

const Error = ({ context }) => <ErrorComponent messageId={context.messageId} />;

Error.propTypes = {
  context: PropTypes.object.isRequired
};

export default Error;

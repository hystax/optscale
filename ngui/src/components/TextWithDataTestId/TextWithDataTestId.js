import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";

const TextWithDataTestId = ({ messageId, children, dataTestId }) => (
  <span data-test-id={dataTestId}>
    {!!messageId && <FormattedMessage id={messageId} />}
    {children}
  </span>
);

TextWithDataTestId.propTypes = {
  messageId: PropTypes.string,
  children: PropTypes.node,
  dataTestId: PropTypes.string.isRequired
};

export default TextWithDataTestId;

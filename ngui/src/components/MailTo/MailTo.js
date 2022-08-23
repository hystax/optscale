import React from "react";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";

const MailTo = ({ email, text, dataTestId }) => (
  <Link data-test-id={dataTestId} href={`mailto:${email}`} rel="noopener">
    {text}
  </Link>
);

MailTo.propTypes = {
  email: PropTypes.string.isRequired,
  text: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  dataTestId: PropTypes.string
};

export default MailTo;

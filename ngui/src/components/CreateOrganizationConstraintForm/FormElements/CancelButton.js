import React from "react";
import PropTypes from "prop-types";
import Button from "components/Button";

const CancelButton = ({ navigateAway }) => <Button dataTestId="btn_cancel" messageId="cancel" onClick={navigateAway} />;

CancelButton.propTypes = {
  navigateAway: PropTypes.func.isRequired
};

export default CancelButton;

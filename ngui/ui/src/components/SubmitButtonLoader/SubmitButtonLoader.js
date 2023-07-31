import React from "react";
import PropTypes from "prop-types";
import ButtonLoader from "components/ButtonLoader";

const SubmitButtonLoader = ({ messageId, isLoading, disabled = false, tooltip = {}, dataTestId, loaderDataTestId }) => (
  <ButtonLoader
    variant="contained"
    messageId={messageId}
    color="primary"
    type="submit"
    isLoading={isLoading}
    dataTestId={dataTestId}
    loaderDataTestId={loaderDataTestId}
    disabled={disabled}
    tooltip={tooltip}
  />
);

SubmitButtonLoader.propTypes = {
  messageId: PropTypes.string.isRequired,
  isLoading: PropTypes.bool.isRequired,
  dataTestId: PropTypes.string,
  loaderDataTestId: PropTypes.string,
  disabled: PropTypes.bool,
  tooltip: PropTypes.object
};

export default SubmitButtonLoader;

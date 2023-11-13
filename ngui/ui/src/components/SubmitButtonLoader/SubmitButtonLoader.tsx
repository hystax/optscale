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

export default SubmitButtonLoader;

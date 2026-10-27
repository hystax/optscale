import ButtonLoader from "components/ButtonLoader";

type SubmitButtonLoaderProps = {
  messageId: string;
  isLoading?: boolean;
  disabled?: boolean;
  tooltip?: Record<string, unknown>;
  dataTestId?: string;
  loaderDataTestId?: string;
  size?: "small" | "medium" | "large";
};

const SubmitButtonLoader = ({
  messageId,
  isLoading,
  disabled = false,
  tooltip = {},
  dataTestId,
  loaderDataTestId,
  size,
}: SubmitButtonLoaderProps) => (
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
    size={size}
  />
);

export default SubmitButtonLoader;

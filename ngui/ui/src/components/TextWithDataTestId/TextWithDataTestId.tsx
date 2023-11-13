import { FormattedMessage } from "react-intl";

const TextWithDataTestId = ({ messageId, children, dataTestId }) => (
  <span data-test-id={dataTestId}>
    {!!messageId && <FormattedMessage id={messageId} />}
    {children}
  </span>
);

export default TextWithDataTestId;

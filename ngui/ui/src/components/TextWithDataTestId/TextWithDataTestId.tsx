import React from "react";
import { FormattedMessage } from "react-intl";

type TextWithDataTestIdProps = {
  dataTestId: string;
  children?: React.ReactNode;
  messageId?: string;
};

const TextWithDataTestId = ({ messageId, children, dataTestId }: TextWithDataTestIdProps) => (
  <span data-test-id={dataTestId}>
    {!!messageId && <FormattedMessage id={messageId} />}
    {children}
  </span>
);

export default TextWithDataTestId;

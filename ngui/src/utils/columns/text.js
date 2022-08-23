import React from "react";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";

const text = ({ headerMessageId, headerDataTestId, accessor, options = {} }) => ({
  Header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  accessor,
  Cell: ({ cell: { value } }) => value,
  ...options
});

export default text;

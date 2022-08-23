import React from "react";
import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import TextWithDataTestId from "components/TextWithDataTestId";

const name = ({ captionAccessor, headerDataTestId, accessor = "name", enableTextCopy = false }) => ({
  Header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="name" />
    </TextWithDataTestId>
  ),
  accessor,
  Cell: ({ row: { original }, cell: { value } }) => (
    <CaptionedCell caption={original[captionAccessor]} enableTextCopy={enableTextCopy}>
      <strong>{value}</strong>
    </CaptionedCell>
  )
});

export default name;

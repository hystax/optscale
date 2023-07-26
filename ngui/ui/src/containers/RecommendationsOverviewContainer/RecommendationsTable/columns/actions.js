import React from "react";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";

const actions = ({ headerDataTestId, cell }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="actions" />
    </TextWithDataTestId>
  ),
  enableSorting: false,
  id: "actions",
  cell
});

export default actions;

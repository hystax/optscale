import React from "react";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";

const size = ({ headerDataTestId, accessor = "flavor" }) => ({
  Header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="size" />
    </TextWithDataTestId>
  ),
  accessor
});

export default size;

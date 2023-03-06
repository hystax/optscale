import React from "react";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";

const recommendedSize = ({ headerDataTestId, accessorKey = "recommended_flavor" }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="recommendedSize" />
    </TextWithDataTestId>
  ),
  accessorKey
});

export default recommendedSize;

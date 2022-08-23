import React from "react";
import { FormattedMessage } from "react-intl";
import RightsizingFlavorCell from "components/RightsizingFlavorCell";
import TextWithDataTestId from "components/TextWithDataTestId";

const rightsizingSize = ({ headerDataTestId, messageId = "size", accessor = "flavor" }) => ({
  Header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={messageId} />
    </TextWithDataTestId>
  ),
  accessor,
  Cell: ({ row: { original } }) => <RightsizingFlavorCell flavorName={original.flavor} flavorCpu={original.cpu} />
});

export default rightsizingSize;

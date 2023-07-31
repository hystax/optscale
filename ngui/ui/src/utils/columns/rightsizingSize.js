import React from "react";
import { FormattedMessage } from "react-intl";
import RightsizingFlavorCell from "components/RightsizingFlavorCell";
import TextWithDataTestId from "components/TextWithDataTestId";

const rightsizingSize = ({ headerDataTestId, messageId = "size", accessorKey = "flavor" }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={messageId} />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({ row: { original } }) => <RightsizingFlavorCell flavorName={original.flavor} flavorCpu={original.cpu} />
});

export default rightsizingSize;

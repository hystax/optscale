import React from "react";
import { FormattedMessage } from "react-intl";
import RightsizingFlavorCell from "components/RightsizingFlavorCell";
import TextWithDataTestId from "components/TextWithDataTestId";

const recommendedRightsizingSize = ({
  headerDataTestId,
  messageId = "recommendedSize",
  accessorKey = "recommended_flavor",
  nameAccessor = "recommended_flavor",
  cpuAccessor = "recommended_flavor_cpu"
}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={messageId} />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({ row: { original } }) => (
    <RightsizingFlavorCell flavorName={original[nameAccessor]} flavorCpu={original[cpuAccessor]} />
  )
});

export default recommendedRightsizingSize;

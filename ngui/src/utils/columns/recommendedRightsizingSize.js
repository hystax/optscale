import React from "react";
import { FormattedMessage } from "react-intl";
import RightsizingFlavorCell from "components/RightsizingFlavorCell";
import TextWithDataTestId from "components/TextWithDataTestId";

const recommendedRightsizingSize = ({
  headerDataTestId,
  messageId = "recommendedSize",
  accessor = "recommended_flavor",
  nameAccessor = "recommended_flavor",
  cpuAccessor = "recommended_flavor_cpu"
}) => ({
  Header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={messageId} />
    </TextWithDataTestId>
  ),
  accessor,
  Cell: ({ row: { original } }) => (
    <RightsizingFlavorCell flavorName={original[nameAccessor]} flavorCpu={original[cpuAccessor]} />
  )
});

export default recommendedRightsizingSize;

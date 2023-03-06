import React from "react";
import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import CloudLabel from "components/CloudLabel";
import TextWithDataTestId from "components/TextWithDataTestId";

const mlExecutorLocation = ({ headerDataTestId = "lbl_location", accessorKey = "cloud_name" } = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="location" />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({
    row: {
      original: { cloud_name: cloudName, cloud_type: cloudType, region }
    }
  }) => (
    <CaptionedCell caption={region}>
      <CloudLabel disableLink name={cloudName} type={cloudType} />
    </CaptionedCell>
  )
});

export default mlExecutorLocation;

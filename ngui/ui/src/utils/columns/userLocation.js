import React from "react";
import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import CloudLabel from "components/CloudLabel";
import TextWithDataTestId from "components/TextWithDataTestId";

const userLocation = ({ headerDataTestId, accessorKey = "cloud_account_name" }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="location" />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({
    row: {
      original: { cloud_account_id: id, cloud_account_name: name, cloud_type: type, region }
    }
  }) => (
    <CaptionedCell caption={region}>
      <CloudLabel id={id} name={name} type={type} />
    </CaptionedCell>
  )
});

export default userLocation;

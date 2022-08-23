import React from "react";
import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import CloudLabel from "components/CloudLabel";
import TextWithDataTestId from "components/TextWithDataTestId";

const userLocation = ({ headerDataTestId, accessor = "cloud_account_name" }) => ({
  Header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="location" />
    </TextWithDataTestId>
  ),
  accessor,
  Cell: ({
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

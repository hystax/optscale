import React from "react";
import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import CloudLabel from "components/CloudLabel";
import TextWithDataTestId from "components/TextWithDataTestId";

const resourceLocation = ({
  headerDataTestId,
  idAccessor = "cloud_account_id",
  typeAccessor = "cloud_type",
  regionAccessor = "region",
  accessor: nameAccessor = "cloud_account_name"
}) => ({
  Header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="location" />
    </TextWithDataTestId>
  ),
  accessor: nameAccessor,
  Cell: ({ row: { original } }) => (
    <CaptionedCell caption={original[regionAccessor]}>
      <CloudLabel id={original[idAccessor]} name={original[nameAccessor]} type={original[typeAccessor]} />
    </CaptionedCell>
  )
});

export default resourceLocation;

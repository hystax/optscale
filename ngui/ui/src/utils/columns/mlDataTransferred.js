import React from "react";
import { FormattedMessage } from "react-intl";
import FormattedDigitalUnit from "components/FormattedDigitalUnit";
import TextWithDataTestId from "components/TextWithDataTestId";

const mlDataTransferred = ({ headerDataTestId = "lbl_data_transferred", accessorKey = "data_transferred" } = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="dataTransferred" />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({ cell }) => <FormattedDigitalUnit value={cell.getValue()} />
});

export default mlDataTransferred;

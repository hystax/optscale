import React from "react";
import { FormattedMessage } from "react-intl";
import FormattedDigitalUnit, { IEC_UNITS } from "components/FormattedDigitalUnit";
import TextWithDataTestId from "components/TextWithDataTestId";

export const ram = () => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_ram">
      <FormattedMessage id="ram" />
    </TextWithDataTestId>
  ),
  accessorKey: "ram",
  cell: ({ cell }) => <FormattedDigitalUnit value={cell.getValue()} baseUnit={IEC_UNITS.GIBIBYTE} />
});

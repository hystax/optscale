import React from "react";
import { FormattedMessage } from "react-intl";
import PowerScheduleValidityPeriod, { stringifiedPowerScheduleValidityPeriod } from "components/PowerScheduleValidityPeriod";
import TextWithDataTestId from "components/TextWithDataTestId";

const powerScheduleValidityPeriod = ({ startDateAccessor, endDateAccessor }) => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_validity_period">
      <FormattedMessage id="validityPeriod" />
    </TextWithDataTestId>
  ),
  id: "validity_period",
  accessorFn: (originalRow) => {
    const { [startDateAccessor]: startDate, [endDateAccessor]: endDate } = originalRow;

    return stringifiedPowerScheduleValidityPeriod({
      startDate,
      endDate
    });
  },
  cell: ({ row: { original } }) => {
    const { [startDateAccessor]: startDate, [endDateAccessor]: endDate } = original;

    return <PowerScheduleValidityPeriod startDate={startDate} endDate={endDate} />;
  }
});

export default powerScheduleValidityPeriod;

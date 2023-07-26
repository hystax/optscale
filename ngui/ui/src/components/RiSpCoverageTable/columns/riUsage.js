import React from "react";
import { FormattedMessage, FormattedNumber } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { round, percentXofY } from "utils/math";

const CellValue = ({ usage, totalUsage }) => {
  const value = round(usage, 1);

  return (
    <>
      <FormattedMessage id="hour" values={{ value }} />
      &nbsp; (
      <FormattedNumber value={percentXofY(value, totalUsage)} format="percentage" />)
    </>
  );
};

const riUsage = ({ totalRiUsageHrs, totalTotalUsageHrs }) => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_ri_usage">
      <FormattedMessage id="riUsage" />
    </TextWithDataTestId>
  ),
  accessorKey: "ri_usage_hrs",
  cell: ({
    cell,
    row: {
      original: { total_usage_hrs: totalUsageHrs }
    }
  }) => <CellValue usage={cell.getValue()} totalUsage={totalUsageHrs} />,
  footer: () => <CellValue usage={totalRiUsageHrs} totalUsage={totalTotalUsageHrs} />
});

export default riUsage;

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

const spUsage = ({ totalSpUsageHrs, totalTotalUsageHrs }) => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_sp_usage">
      <FormattedMessage id="spUsage" />
    </TextWithDataTestId>
  ),
  accessorKey: "sp_usage_hrs",
  cell: ({
    cell,
    row: {
      original: { total_usage_hrs: totalUsageHrs }
    }
  }) => <CellValue usage={cell.getValue()} totalUsage={totalUsageHrs} />,
  footer: () => <CellValue usage={totalSpUsageHrs} totalUsage={totalTotalUsageHrs} />
});

export default spUsage;

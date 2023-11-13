import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { round } from "utils/math";

const CellValue = ({ usage }) => (
  <FormattedMessage
    id="hour"
    values={{
      value: round(usage, 1)
    }}
  />
);

const totalUsage = ({ totalTotalUsageHrs }) => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_total">
      <FormattedMessage id="totalUsage" />
    </TextWithDataTestId>
  ),
  accessorKey: "total_usage_hrs",
  cell: ({ cell }) => <CellValue usage={cell.getValue()} />,
  footer: () => <CellValue usage={totalTotalUsageHrs} />
});

export default totalUsage;

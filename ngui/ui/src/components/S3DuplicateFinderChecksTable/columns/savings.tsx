import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import { STATUS } from "components/S3DuplicateFinderCheck/utils";
import TextWithDataTestId from "components/TextWithDataTestId";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { CELL_EMPTY_VALUE } from "utils/tables";

const Savings = ({ stats }) => {
  const { monthly_savings: monthlySavings } = stats;

  return <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={monthlySavings} />;
};

const savings = () => ({
  header: (
    <TextWithDataTestId dataTestId="savings">
      <FormattedMessage id="savings" />
    </TextWithDataTestId>
  ),
  id: "saving",
  cell: ({
    row: {
      original: { stats, status }
    }
  }) => (status === STATUS.SUCCESS ? <Savings stats={stats} /> : CELL_EMPTY_VALUE)
});

export default savings;

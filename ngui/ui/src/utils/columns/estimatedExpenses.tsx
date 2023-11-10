import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import { FORMATTED_MONEY_TYPES } from "utils/constants";

const estimatedExpenses = ({ headerDataTestId = "lbl_estimated_savings", accessorKey = "estimated_expenses" } = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="estimatedExpenses" />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({ cell }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue()} />
});

export default estimatedExpenses;

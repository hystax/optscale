import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import { FORMATTED_MONEY_TYPES } from "utils/constants";

type CellRowData = { cell: { getValue: () => number } };

type PossibleMonthlySavingsConfig = {
  headerDataTestId?: string;
  accessorKey?: string;
  defaultSort?: "asc" | "desc";
};

const possibleMonthlySavings = ({
  headerDataTestId,
  accessorKey = "saving",
  defaultSort = "desc",
}: PossibleMonthlySavingsConfig = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="possibleMonthlySavings" />
    </TextWithDataTestId>
  ),
  accessorKey,
  defaultSort,
  cell: ({ cell }: CellRowData) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue()} />,
});

export default possibleMonthlySavings;

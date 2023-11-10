import { useSearchParams } from "react-router-dom";
import { CostExplorerMocked } from "components/CostExplorer";
import {
  ExpensesBreakdownForPoolMocked,
  ExpensesBreakdownForCloudMocked,
  ExpensesBreakdownForOwnerMocked
} from "components/ExpensesBreakdown";
import Mocked from "components/Mocked";
import PoolExpensesBreakdownContainer from "containers/PoolExpensesBreakdownContainer";
import { COST_EXPLORER, EXPENSES_FILTERBY_TYPES, FILTER_BY } from "utils/constants";

const getMockupComponent = (filterBy) =>
  ({
    [COST_EXPLORER]: <CostExplorerMocked />,
    [EXPENSES_FILTERBY_TYPES.CLOUD]: <ExpensesBreakdownForCloudMocked />,
    [EXPENSES_FILTERBY_TYPES.POOL]: <ExpensesBreakdownForPoolMocked />,
    [EXPENSES_FILTERBY_TYPES.EMPLOYEE]: <ExpensesBreakdownForOwnerMocked />
  })[filterBy];

const Expenses = () => {
  const [searchParams] = useSearchParams();

  const filterBy = searchParams.get(FILTER_BY) ?? COST_EXPLORER;

  return (
    <Mocked mock={getMockupComponent(filterBy)}>
      <PoolExpensesBreakdownContainer type={COST_EXPLORER} />
    </Mocked>
  );
};

export default Expenses;

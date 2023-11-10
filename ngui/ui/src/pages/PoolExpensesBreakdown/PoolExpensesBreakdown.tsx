import { useParams } from "react-router-dom";
import PoolExpensesBreakdownContainer from "containers/PoolExpensesBreakdownContainer";
import { POOL_DETAILS } from "utils/constants";

const PoolExpensesBreakdown = () => {
  const { poolId } = useParams();

  return <PoolExpensesBreakdownContainer type={POOL_DETAILS} entityId={poolId} />;
};

export default PoolExpensesBreakdown;

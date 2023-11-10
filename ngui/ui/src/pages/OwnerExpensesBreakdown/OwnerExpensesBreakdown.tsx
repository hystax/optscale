import { useParams } from "react-router-dom";
import EmployeeExpensesBreakdownContainer from "containers/EmployeeExpensesBreakdownContainer";
import { OWNER_DETAILS } from "utils/constants";

const OwnerExpensesBreakdown = () => {
  const { employeeId } = useParams();

  return <EmployeeExpensesBreakdownContainer type={OWNER_DETAILS} entityId={employeeId} />;
};

export default OwnerExpensesBreakdown;

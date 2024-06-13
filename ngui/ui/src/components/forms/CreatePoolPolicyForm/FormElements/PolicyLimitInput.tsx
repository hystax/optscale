import { isExpensesLimit, isTtlLimit } from "utils/constraints";
import ExpenseLimitInput from "./ExpenseLimitInput";
import TtlLimitInput from "./TtlLimitInput";

const CreatePoolPolicyPoolSelector = ({ policyType }) => {
  if (isExpensesLimit(policyType)) {
    return <ExpenseLimitInput />;
  }
  if (isTtlLimit(policyType)) {
    return <TtlLimitInput />;
  }
  return null;
};

export default CreatePoolPolicyPoolSelector;

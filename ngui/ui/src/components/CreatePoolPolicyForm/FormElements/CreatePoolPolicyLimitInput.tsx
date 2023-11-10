import {
  EditPoolPolicyLimitFormExpenseLimitInput,
  EditPoolPolicyLimitFormTtlLimitInput
} from "components/EditPoolPolicyLimitForm/FormElements";
import { isExpensesLimit, isTtlLimit } from "utils/constraints";

const CreatePoolPolicyPoolSelector = ({ policyType, name }) => {
  if (isExpensesLimit(policyType)) {
    return <EditPoolPolicyLimitFormExpenseLimitInput name={name} enableLabel />;
  }
  if (isTtlLimit(policyType)) {
    return <EditPoolPolicyLimitFormTtlLimitInput name={name} enableLabel />;
  }
  return null;
};

export default CreatePoolPolicyPoolSelector;

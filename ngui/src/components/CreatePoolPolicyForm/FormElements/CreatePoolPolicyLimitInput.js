import React from "react";
import PropTypes from "prop-types";
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

CreatePoolPolicyPoolSelector.propTypes = {
  name: PropTypes.string.isRequired,
  policyType: PropTypes.string.isRequired
};

export default CreatePoolPolicyPoolSelector;

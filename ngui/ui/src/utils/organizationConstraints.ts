import { ANOMALY_TYPES, QUOTAS_AND_BUDGETS_TYPES, TAGGING_POLICY_TYPES } from "./constants";
import { isEmpty as isEmptyObject } from "./objects";

export const hasStatusInformation = (constraint) =>
  constraint.last_run !== 0 && constraint.last_run_result && !isEmptyObject(constraint.last_run_result);

export const isAnomalyConstraint = (type: string) => Object.keys(ANOMALY_TYPES).includes(type);

export const isQuotasAndBudgetsConstraint = (type: string) => Object.keys(QUOTAS_AND_BUDGETS_TYPES).includes(type);

export const isTaggingPolicyConstraint = (type: string) => Object.keys(TAGGING_POLICY_TYPES).includes(type);

export const isAnomalyConstraintViolated = (constraint) => {
  const {
    last_run_result: { average, today },
    definition: { threshold }
  } = constraint;

  return today > average + (average * threshold) / 100;
};

export const isQuotasAndBudgetsConstraintViolated = (constraint) => {
  const {
    last_run_result: { current, limit }
  } = constraint;

  return current > limit;
};

export const isTaggingPolicyConstraintViolated = (constraint) => {
  const {
    last_run_result: { value }
  } = constraint;

  return value !== 0;
};

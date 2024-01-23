import OrganizationConstraintsCard from "components/OrganizationConstraintsCard";
import OrganizationConstraintsService from "services/OrganizationConstraintsService";
import { ANOMALY_TYPES, QUOTAS_AND_BUDGETS_TYPES, TAGGING_POLICY_TYPES } from "utils/constants";
import {
  hasStatusInformation,
  isAnomalyConstraint,
  isAnomalyConstraintViolated,
  isQuotasAndBudgetsConstraint,
  isQuotasAndBudgetsConstraintViolated,
  isTaggingPolicyConstraint,
  isTaggingPolicyConstraintViolated
} from "utils/organizationConstraints";

const filterViolatedConstraints = (constraint) => {
  switch (true) {
    case isAnomalyConstraint(constraint.type): {
      return isAnomalyConstraintViolated(constraint);
    }
    case isQuotasAndBudgetsConstraint(constraint.type): {
      return isQuotasAndBudgetsConstraintViolated(constraint);
    }
    case isTaggingPolicyConstraint(constraint.type): {
      return isTaggingPolicyConstraintViolated(constraint);
    }
    default:
      return false;
  }
};

const CONSTRAINT_TYPES = Object.freeze(
  Object.keys({
    ...ANOMALY_TYPES,
    ...QUOTAS_AND_BUDGETS_TYPES,
    ...TAGGING_POLICY_TYPES
  })
);

const OrganizationConstraintsCardContainer = () => {
  const { useGetAll } = OrganizationConstraintsService();

  const { isLoading, constraints } = useGetAll(CONSTRAINT_TYPES);

  const filteredConstraints = constraints.filter(hasStatusInformation).filter(filterViolatedConstraints);

  return <OrganizationConstraintsCard constraints={filteredConstraints} isLoading={isLoading} />;
};

export default OrganizationConstraintsCardContainer;

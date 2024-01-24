import OrganizationConstraintsCard from "components/OrganizationConstraintsCard";
import OrganizationConstraintsService from "services/OrganizationConstraintsService";
import { ANOMALIES, QUOTAS_AND_BUDGETS, TAGGING_POLICIES } from "urls";
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

const CONSTRAINT_TYPES = Object.freeze(
  Object.keys({
    ...ANOMALY_TYPES,
    ...QUOTAS_AND_BUDGETS_TYPES,
    ...TAGGING_POLICY_TYPES
  })
);

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

const addConstraintMessageIdAndLink = (constraint) => {
  const getMessageIdAndLink = () => {
    const constraintType = constraint.type;

    switch (true) {
      case isAnomalyConstraint(constraintType): {
        return {
          typeMessageId: "anomaly",
          typeLink: ANOMALIES
        };
      }
      case isQuotasAndBudgetsConstraint(constraintType): {
        return {
          typeMessageId: "quota/Budget",
          typeLink: QUOTAS_AND_BUDGETS
        };
      }
      case isTaggingPolicyConstraint(constraintType): {
        return {
          typeMessageId: "tagging",
          typeLink: TAGGING_POLICIES
        };
      }
      default:
        return {};
    }
  };

  return {
    ...constraint,
    ...getMessageIdAndLink()
  };
};

const OrganizationConstraintsCardContainer = () => {
  const { useGetAll } = OrganizationConstraintsService();

  const { isLoading, constraints } = useGetAll(CONSTRAINT_TYPES);

  const preparedConstraints = constraints
    .filter(hasStatusInformation)
    .filter(filterViolatedConstraints)
    .map(addConstraintMessageIdAndLink);

  return <OrganizationConstraintsCard constraints={preparedConstraints} isLoading={isLoading} />;
};

export default OrganizationConstraintsCardContainer;

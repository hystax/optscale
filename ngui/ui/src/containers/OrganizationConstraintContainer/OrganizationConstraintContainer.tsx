import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useParams, Link as RouterLink } from "react-router-dom";
import OrganizationConstraint from "components/OrganizationConstraint";
import OrganizationConstraintsService from "services/OrganizationConstraintsService";
import { ANOMALIES, QUOTAS_AND_BUDGETS, TAGGING_POLICIES } from "urls";

const OrganizationConstraintContainer = () => {
  const { useGetOne } = OrganizationConstraintsService();

  // container is used on two pages with two different params ids
  const { anomalyId, policyId, taggingPolicyId } = useParams();
  const constraintId = anomalyId || policyId || taggingPolicyId;
  const { constraint, isLoading } = useGetOne(constraintId);

  let actionBarTitleDefinition;
  let actionBarBreadcrumbsDefinition;

  if (anomalyId) {
    actionBarBreadcrumbsDefinition = [
      <Link key={1} to={ANOMALIES} component={RouterLink}>
        <FormattedMessage id="anomalyDetectionTitle" />
      </Link>
    ];
    actionBarTitleDefinition = {
      text: <FormattedMessage id="anomalyDetectionPolicyTitle" />,
      dataTestId: "lbl_anomaly_detection_policy"
    };
  }

  if (policyId) {
    actionBarBreadcrumbsDefinition = [
      <Link key={1} to={QUOTAS_AND_BUDGETS} component={RouterLink}>
        <FormattedMessage id="quotasAndBudgetsTitle" />
      </Link>
    ];
    actionBarTitleDefinition = {
      text: <FormattedMessage id="quotaAndBudgetPolicyTitle" />,
      dataTestId: "lbl_quota_and_budget_policy"
    };
  }

  if (taggingPolicyId) {
    actionBarBreadcrumbsDefinition = [
      <Link key={1} to={TAGGING_POLICIES} component={RouterLink}>
        <FormattedMessage id="taggingPolicy.taggingPoliciesTitle" />
      </Link>
    ];
    actionBarTitleDefinition = {
      text: <FormattedMessage id="taggingPolicyTitle" />,
      dataTestId: "lbl_tagging_policy"
    };
  }

  return (
    <OrganizationConstraint
      actionBarBreadcrumbsDefinition={actionBarBreadcrumbsDefinition}
      actionBarTitleDefinition={actionBarTitleDefinition}
      constraint={constraint}
      isLoading={isLoading}
    />
  );
};

export default OrganizationConstraintContainer;

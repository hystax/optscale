import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useParams, Link as RouterLink } from "react-router-dom";
import OrganizationConstraint from "components/OrganizationConstraint";
import OrganizationConstraintsService from "services/OrganizationConstraintsService";
import OrganizationsLimitHitsService from "services/OrganizationsLimitHitsService";
import { ANOMALIES, QUOTAS_AND_BUDGETS, TAGGING_POLICIES } from "urls";

const getActionBarProperties = ({
  anomalyId,
  policyId,
  taggingPolicyId
}: {
  anomalyId?: string;
  policyId?: string;
  taggingPolicyId?: string;
}) => {
  switch (true) {
    case !!anomalyId:
      return {
        actionBarBreadcrumbsDefinition: [
          <Link key={1} to={ANOMALIES} component={RouterLink}>
            <FormattedMessage id="anomalyDetectionTitle" />
          </Link>
        ],
        actionBarTitleDefinition: {
          text: <FormattedMessage id="anomalyDetectionPolicyTitle" />,
          dataTestId: "lbl_anomaly_detection_policy"
        }
      };
    case !!policyId:
      return {
        actionBarBreadcrumbsDefinition: [
          <Link key={1} to={QUOTAS_AND_BUDGETS} component={RouterLink}>
            <FormattedMessage id="quotasAndBudgetsTitle" />
          </Link>
        ],
        actionBarTitleDefinition: {
          text: <FormattedMessage id="quotaAndBudgetPolicyTitle" />,
          dataTestId: "lbl_quota_and_budget_policy"
        }
      };
    case !!taggingPolicyId:
      return {
        actionBarBreadcrumbsDefinition: [
          <Link key={1} to={TAGGING_POLICIES} component={RouterLink}>
            <FormattedMessage id="taggingPolicy.taggingPoliciesTitle" />
          </Link>
        ],
        actionBarTitleDefinition: {
          text: <FormattedMessage id="taggingPolicyTitle" />,
          dataTestId: "lbl_tagging_policy"
        }
      };

    default:
      return {
        actionBarBreadcrumbsDefinition: undefined,
        actionBarTitleDefinition: undefined
      };
  }
};

const OrganizationConstraintContainer = () => {
  const { useGetOne } = OrganizationConstraintsService();
  const { useGet: useGetLimitHits } = OrganizationsLimitHitsService();

  // container is used on two pages with two different params ids
  const { anomalyId, policyId, taggingPolicyId } = useParams();
  const constraintId = anomalyId || policyId || taggingPolicyId;
  const { constraint, isLoading: isGetConstraintLoading } = useGetOne(constraintId);

  const { data: limitHits, isLoading: isGetLimitHitsLoading } = useGetLimitHits(constraintId);

  const { actionBarBreadcrumbsDefinition, actionBarTitleDefinition } = getActionBarProperties({
    anomalyId,
    policyId,
    taggingPolicyId
  });

  return (
    <OrganizationConstraint
      actionBarBreadcrumbsDefinition={actionBarBreadcrumbsDefinition}
      actionBarTitleDefinition={actionBarTitleDefinition}
      constraint={constraint}
      limitHits={limitHits}
      isLoadingProps={{
        isGetConstraintLoading,
        isGetLimitHitsLoading
      }}
    />
  );
};

export default OrganizationConstraintContainer;

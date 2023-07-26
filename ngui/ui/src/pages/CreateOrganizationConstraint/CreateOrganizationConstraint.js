import React from "react";
import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useLocation, Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import Protector from "components/Protector";
import CreateOrganizationConstraintFormContainer from "containers/CreateOrganizationConstraintFormContainer";
import {
  ANOMALIES,
  ANOMALY_CREATE,
  QUOTAS_AND_BUDGETS,
  QUOTA_AND_BUDGET_CREATE,
  TAGGING_POLICIES,
  TAGGING_POLICY_CREATE
} from "urls";
import { ANOMALY_TYPES, QUOTAS_AND_BUDGETS_TYPES, TAGGING_POLICY_TYPES } from "utils/constants";

const properties = {
  [ANOMALY_CREATE]: {
    types: Object.keys(ANOMALY_TYPES),
    navigateAwayLink: ANOMALIES,
    actionBar: {
      breadcrumbs: [
        <Link key={1} to={ANOMALIES} component={RouterLink}>
          <FormattedMessage id="anomalyDetectionTitle" />
        </Link>
      ],
      title: {
        text: <FormattedMessage id="createAnomalyDetectionPolicyTitle" />,
        dataTestId: "lbl_create_anomaly_detection_policy"
      }
    }
  },
  [QUOTA_AND_BUDGET_CREATE]: {
    types: Object.keys(QUOTAS_AND_BUDGETS_TYPES),
    navigateAwayLink: QUOTAS_AND_BUDGETS,
    actionBar: {
      breadcrumbs: [
        <Link key={1} to={QUOTAS_AND_BUDGETS} component={RouterLink}>
          <FormattedMessage id="quotasAndBudgetsTitle" />
        </Link>
      ],
      title: {
        text: <FormattedMessage id="createQuotaAndBudgetPolicyTitle" />,
        dataTestId: "lbl_create_quota_and_budget_policy"
      }
    }
  },
  [TAGGING_POLICY_CREATE]: {
    types: Object.keys(TAGGING_POLICY_TYPES),
    navigateAwayLink: TAGGING_POLICIES,
    actionBar: {
      breadcrumbs: [
        <Link key={1} to={TAGGING_POLICIES} component={RouterLink}>
          <FormattedMessage id="taggingPolicy.taggingPoliciesTitle" />
        </Link>
      ],
      title: {
        text: <FormattedMessage id="taggingPolicy.createTaggingPolicyTitle" />,
        dataTestId: "lbl_create_tagging_policy"
      }
    }
  }
};
const getProperties = (pathname) => properties[pathname];

const CreateOrganizationConstraint = () => {
  const { pathname } = useLocation();
  const { actionBar, types, navigateAwayLink } = getProperties(pathname);
  return (
    <Protector allowedActions={["EDIT_PARTNER"]}>
      <ActionBar data={actionBar} />
      <PageContentWrapper>
        <CreateOrganizationConstraintFormContainer navigateAwayLink={navigateAwayLink} types={types} />
      </PageContentWrapper>
    </Protector>
  );
};

export default CreateOrganizationConstraint;

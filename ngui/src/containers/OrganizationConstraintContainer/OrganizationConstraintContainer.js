import React from "react";
import { useParams } from "react-router-dom";
import OrganizationConstraint from "components/OrganizationConstraint";
import OrganizationConstraintsService from "services/OrganizationConstraintsService";

const OrganizationConstraintContainer = () => {
  const { useGetOne } = OrganizationConstraintsService();

  // container is used on two pages with two different params ids
  const { anomalyId, policyId, taggingPolicyId } = useParams();
  const constraintId = anomalyId || policyId || taggingPolicyId;
  const { constraint, isLoading } = useGetOne(constraintId);

  let actionBarTitleDefinition;

  if (anomalyId) {
    actionBarTitleDefinition = {
      messageId: "anomalyDetectionPolicyTitle",
      dataTestId: "lbl_anomaly_detection_policy"
    };
  }

  if (policyId) {
    actionBarTitleDefinition = {
      messageId: "quotaAndBudgetPolicyTitle",
      dataTestId: "lbl_quota_and_budget_policy"
    };
  }

  if (taggingPolicyId) {
    actionBarTitleDefinition = {
      messageId: "taggingPolicyTitle",
      dataTestId: "lbl_tagging_policy"
    };
  }

  return (
    <OrganizationConstraint actionBarTitleDefinition={actionBarTitleDefinition} constraint={constraint} isLoading={isLoading} />
  );
};

export default OrganizationConstraintContainer;

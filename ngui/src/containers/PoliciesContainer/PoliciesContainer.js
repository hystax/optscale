import React, { useMemo } from "react";
import Mocked from "components/Mocked";
import OrganizationConstraints from "components/OrganizationConstraints";
import OrganizationConstraintsMocked from "components/OrganizationConstraintsMocked";
import OrganizationConstraintsService from "services/OrganizationConstraintsService";
import { QUOTA_AND_BUDGET_CREATE } from "urls";
import { QUOTAS_AND_BUDGETS_TYPES } from "utils/constants";

const actionBarDefinition = {
  title: {
    messageId: "quotasAndBudgetsTitle",
    dataTestId: "lbl_constraints_quotas_and_budgets"
  }
};

const PoliciesContainer = () => {
  const { useGetAll } = OrganizationConstraintsService();
  const types = useMemo(() => Object.keys(QUOTAS_AND_BUDGETS_TYPES), []);
  const { isLoading, constraints } = useGetAll(types);

  return (
    <Mocked mock={<OrganizationConstraintsMocked actionBarDefinition={actionBarDefinition} />}>
      <OrganizationConstraints
        actionBarDefinition={actionBarDefinition}
        constraints={constraints}
        isLoading={isLoading}
        addButtonLink={QUOTA_AND_BUDGET_CREATE}
      />
    </Mocked>
  );
};

PoliciesContainer.propTypes = {};

export default PoliciesContainer;

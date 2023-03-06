import React, { useMemo } from "react";
import Mocked, { MESSAGE_TYPES } from "components/Mocked";
import OrganizationConstraints from "components/OrganizationConstraints";
import OrganizationConstraintsMocked from "components/OrganizationConstraintsMocked";
import { useShouldRenderConnectCloudAccountMock } from "hooks/useShouldRenderConnectCloudAccountMock";
import OrganizationConstraintsService from "services/OrganizationConstraintsService";
import { QUOTA_AND_BUDGET_CREATE } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
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

  const shouldRenderConnectCloudAccountMock = useShouldRenderConnectCloudAccountMock();

  const getBackdropMessageType = () => {
    if (shouldRenderConnectCloudAccountMock) {
      return MESSAGE_TYPES.CLOUD_ACCOUNTS;
    }
    if (isEmptyArray(constraints)) {
      return MESSAGE_TYPES.QUOTAS_AND_BUDGETS_POLICY;
    }
    return undefined;
  };

  return (
    <Mocked
      mockCondition={!isLoading && isEmptyArray(constraints)}
      backdropMessageType={getBackdropMessageType()}
      mock={<OrganizationConstraintsMocked actionBarDefinition={actionBarDefinition} />}
    >
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

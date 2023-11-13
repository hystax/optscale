import { useMemo } from "react";
import Mocked, { MESSAGE_TYPES } from "components/Mocked";
import OrganizationConstraints from "components/OrganizationConstraints";
import OrganizationConstraintsMocked from "components/OrganizationConstraintsMocked";
import { useShouldRenderConnectCloudAccountMock } from "hooks/useShouldRenderConnectCloudAccountMock";
import OrganizationConstraintsService from "services/OrganizationConstraintsService";
import { TAGGING_POLICY_CREATE } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { TAGGING_POLICY_TYPES } from "utils/constants";

const actionBarDefinition = {
  title: {
    messageId: "taggingPolicy.taggingPoliciesTitle",
    dataTestId: "lbl_tagging_policies"
  }
};

const TaggingPoliciesContainer = () => {
  const { useGetAll } = OrganizationConstraintsService();
  const types = useMemo(() => Object.keys(TAGGING_POLICY_TYPES), []);
  const { isLoading, constraints } = useGetAll(types);

  const shouldRenderConnectCloudAccountMock = useShouldRenderConnectCloudAccountMock();

  const getBackdropMessageType = () => {
    if (shouldRenderConnectCloudAccountMock) {
      return MESSAGE_TYPES.CLOUD_ACCOUNTS;
    }
    if (isEmptyArray(constraints)) {
      return MESSAGE_TYPES.TAGGING_POLICY;
    }
    return undefined;
  };

  return (
    <Mocked
      mockCondition={(!isLoading && isEmptyArray(constraints)) || shouldRenderConnectCloudAccountMock}
      backdropMessageType={getBackdropMessageType()}
      mock={<OrganizationConstraintsMocked actionBarDefinition={actionBarDefinition} />}
    >
      <OrganizationConstraints
        actionBarDefinition={actionBarDefinition}
        constraints={constraints}
        isLoading={isLoading}
        addButtonLink={TAGGING_POLICY_CREATE}
      />
    </Mocked>
  );
};

export default TaggingPoliciesContainer;

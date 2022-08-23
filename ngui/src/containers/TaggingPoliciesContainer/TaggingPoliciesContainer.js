import React, { useMemo } from "react";
import Mocked from "components/Mocked";
import OrganizationConstraints from "components/OrganizationConstraints";
import OrganizationConstraintsMocked from "components/OrganizationConstraintsMocked";
import OrganizationConstraintsService from "services/OrganizationConstraintsService";
import { TAGGING_POLICY_CREATE } from "urls";
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

  return (
    <Mocked mock={<OrganizationConstraintsMocked actionBarDefinition={actionBarDefinition} />}>
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

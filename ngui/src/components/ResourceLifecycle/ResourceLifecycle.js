import React from "react";
import ActionBar from "components/ActionBar";
import Mocked from "components/Mocked";
import PageContentWrapper from "components/PageContentWrapper";
import ResourceLifecycleGlobalPoolPoliciesContainerMocked from "components/ResourceLifecycleGlobalPoolPoliciesContainerMocked";
import TabsWrapper from "components/TabsWrapper";
import ResourceLifecycleGlobalPoolPoliciesContainer from "containers/ResourceLifecycleGlobalPoolPoliciesContainer";
import ResourceLifecycleGlobalResourceConstraintsContainer from "containers/ResourceLifecycleGlobalResourceConstraintsContainer";

const actionBarDefinition = {
  title: {
    messageId: "resourceLifecycleTitle",
    dataTestId: "lbl_resource_lifecycle_detection"
  }
};

const TABS = Object.freeze({
  POOL_POLICIES: "poolPolicies",
  RESOURCE_CONSTRAINTS: "resourceConstraints"
});

const tabs = [
  {
    title: TABS.POOL_POLICIES,
    node: (
      <Mocked mock={<ResourceLifecycleGlobalPoolPoliciesContainerMocked />} backdropCondition={false}>
        <ResourceLifecycleGlobalPoolPoliciesContainer />
      </Mocked>
    ),
    dataTestId: "btn_tab_pool_policies"
  },
  {
    title: TABS.RESOURCE_CONSTRAINTS,
    node: <ResourceLifecycleGlobalResourceConstraintsContainer />,
    dataTestId: "btn_tab_resource_constraints"
  }
];

const ResourceLifecycle = () => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <TabsWrapper
        tabsProps={{
          tabs,
          defaultTab: TABS.POOL_POLICIES,
          name: "resource-lifecycle",
          queryParamsOnChangeBlacklist: ["search"]
        }}
      />
    </PageContentWrapper>
  </>
);

ResourceLifecycle.propTypes = {};

export default ResourceLifecycle;

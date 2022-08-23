import React from "react";
import ResourceLifecycleGlobalPoolPolicies from "components/ResourceLifecycleGlobalPoolPolicies";
import GlobalConstraintsService from "services/GlobalConstraintsService";

const ResourceLifecycleGlobalPoolPoliciesContainer = () => {
  const { useGetPoolPolicies } = GlobalConstraintsService();

  const { isLoading, policies } = useGetPoolPolicies();

  return <ResourceLifecycleGlobalPoolPolicies isLoading={isLoading} poolPolicies={policies} />;
};

export default ResourceLifecycleGlobalPoolPoliciesContainer;

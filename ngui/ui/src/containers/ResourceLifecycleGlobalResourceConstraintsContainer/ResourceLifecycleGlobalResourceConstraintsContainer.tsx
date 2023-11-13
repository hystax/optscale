import ResourceLifecycleGlobalResourceConstraints from "components/ResourceLifecycleGlobalResourceConstraints";
import GlobalConstraintsService from "services/GlobalConstraintsService";

const ResourceLifecycleGlobalResourceConstraintsContainer = () => {
  const { useGetResourceConstraints } = GlobalConstraintsService();

  const { isLoading, constraints } = useGetResourceConstraints();

  return <ResourceLifecycleGlobalResourceConstraints isLoading={isLoading} constraints={constraints} />;
};

export default ResourceLifecycleGlobalResourceConstraintsContainer;

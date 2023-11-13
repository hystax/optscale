import { useParams } from "react-router-dom";
import ResourceContainer from "containers/ResourceContainer";

const Resource = () => {
  const { resourceId } = useParams();

  return (
    <ResourceContainer
      /*
        Use resourceId as a key in order to reset local state 
        when navigating to between resources the same route, 
        e.g between cluster and its sub-resources and vice versa
      */
      key={resourceId}
      resourceId={resourceId}
    />
  );
};

export default Resource;

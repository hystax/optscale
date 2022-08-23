import React from "react";
import { useParams } from "react-router-dom";
import ResourceContainer from "containers/ResourceContainer";

const Resource = () => {
  const { resourceId } = useParams();

  return <ResourceContainer resourceId={resourceId} />;
};

export default Resource;

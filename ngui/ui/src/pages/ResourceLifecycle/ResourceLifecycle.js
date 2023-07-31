import React from "react";
import Mocked from "components/Mocked";
import ResourceLifecycleComponent from "components/ResourceLifecycle";

const ResourceLifecycle = () => (
  <Mocked mock={<ResourceLifecycleComponent />}>
    <ResourceLifecycleComponent />
  </Mocked>
);

export default ResourceLifecycle;

import React from "react";
import { ClusterTypesMocked } from "components/ClusterTypes";
import Mocked from "components/Mocked";
import ClusterTypesContainer from "containers/ClusterTypesContainer";

const ClusterTypes = () => (
  <Mocked mock={<ClusterTypesMocked />}>
    <ClusterTypesContainer />
  </Mocked>
);

export default ClusterTypes;

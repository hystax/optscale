import React from "react";
import { useParams } from "react-router-dom";
import OrganizationOverviewContainer from "containers/OrganizationOverviewContainer";

const OrganizationOverview = () => {
  const { poolId } = useParams();

  return <OrganizationOverviewContainer poolId={poolId} />;
};

export default OrganizationOverview;

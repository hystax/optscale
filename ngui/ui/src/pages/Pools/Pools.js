import React from "react";
import Redirector from "components/Redirector";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { getPoolUrl } from "urls";

const Pools = () => {
  const { organizationPoolId } = useOrganizationInfo();
  return <Redirector condition to={getPoolUrl(organizationPoolId)} />;
};

export default Pools;

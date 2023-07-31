import React from "react";
import { useParams } from "react-router-dom";
import CloudAccountDetailsContainer from "containers/CloudAccountDetailsContainer";

const CloudAccountDetails = () => {
  const { cloudAccountId } = useParams();

  return <CloudAccountDetailsContainer cloudAccountId={cloudAccountId} />;
};

export default CloudAccountDetails;

import React from "react";
import { useParams } from "react-router-dom";
import CreatePoolFormContainer from "containers/CreatePoolFormContainer";

const CreatePool = () => {
  const { poolId } = useParams();

  return <CreatePoolFormContainer parentPoolId={poolId} />;
};

export default CreatePool;

import React from "react";
import { useParams } from "react-router-dom";
import EditPoolFormContainer from "containers/EditPoolFormContainer";

const EditPool = () => {
  const { poolId } = useParams();

  return <EditPoolFormContainer poolId={poolId} />;
};

export default EditPool;

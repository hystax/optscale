import React from "react";
import Configure from "components/Configure";
import SpinnerLoader from "components/SpinnerLoader";
import { useIsUserConnectedToOptscale } from "hooks/useIsUserConnectedToOptscale";

const ConfigureContainer = () => {
  const { loading, refetch, error, data } = useIsUserConnectedToOptscale();

  if (loading) {
    return <SpinnerLoader />;
  }
  if (error) {
    return "Something went wrong :(";
  }
  if (!data) {
    return null;
  }

  return <Configure isConnected={data.isConnected} refresh={() => refetch()} />;
};

export default ConfigureContainer;

import React, { useEffect } from "react";
import { GET_TOKEN } from "api/auth/actionTypes";
import Redirector from "components/Redirector";
import { useApiData } from "hooks/useApiData";
import { useSignOut } from "hooks/useSignOut";
import { getUrlWithNextQueryParam, LOGIN } from "urls";
import { getQueryParams } from "utils/network";

const Signout = () => {
  const { dispatchReset, cancelAllPendingRequests } = useSignOut();

  const {
    apiData: { token }
  } = useApiData(GET_TOKEN);

  useEffect(() => {
    dispatchReset();
  }, [dispatchReset]);

  useEffect(() => {
    cancelAllPendingRequests();
  }, [cancelAllPendingRequests]);

  return <Redirector condition={!token} to={getUrlWithNextQueryParam(LOGIN, getQueryParams().next)} replace />;
};

export default Signout;

import { Navigate } from "react-router-dom";
import { useGetToken } from "hooks/useGetToken";
import { NEXT_QUERY_PARAMETER_NAME, HOME, USER_EMAIL_QUERY_PARAMETER_NAME, SHOW_POLICY_QUERY_PARAM } from "urls";
import { getSearchParams } from "utils/network";
import { Loading } from "../../common";

const getRedirectionPath = (scopeUserEmail: string) => {
  const {
    [NEXT_QUERY_PARAMETER_NAME]: next = HOME,
    [USER_EMAIL_QUERY_PARAMETER_NAME]: userEmailQueryParameter,
    [SHOW_POLICY_QUERY_PARAM]: showPolicyQueryParameter = false,
  } = getSearchParams() as {
    [NEXT_QUERY_PARAMETER_NAME]: string;
    [USER_EMAIL_QUERY_PARAMETER_NAME]: string;
    [SHOW_POLICY_QUERY_PARAM]: string;
  };

  const getNextPath = () => {
    if (userEmailQueryParameter) {
      return userEmailQueryParameter === scopeUserEmail ? next : HOME;
    }

    return next;
  };

  const nextPath = getNextPath();

  const url = new URL(nextPath, window.location.origin);

  // Add showPolicy param if needed
  if (showPolicyQueryParameter) {
    url.searchParams.set(SHOW_POLICY_QUERY_PARAM, showPolicyQueryParameter);
  }

  // Return just the pathname and search parts, removing the origin
  return `${url.pathname}${url.search}`;
};

const ProceedToApplication = () => {
  const { userEmail } = useGetToken();

  return (
    <>
      <Loading />
      <Navigate to={getRedirectionPath(userEmail)} />
    </>
  );
};

export default ProceedToApplication;

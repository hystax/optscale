import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getInvitations } from "api";
import { GET_TOKEN } from "api/auth/actionTypes";
import { GET_INVITATIONS } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";

export const useGet = () => {
  const dispatch = useDispatch();

  const { isLoading, shouldInvoke } = useApiState(GET_INVITATIONS);
  const {
    apiData: { userId }
  } = useApiData(GET_TOKEN);

  useEffect(() => {
    if (shouldInvoke && userId) {
      dispatch(getInvitations());
    }
  }, [dispatch, shouldInvoke, userId]);

  const { apiData: invitations } = useApiData(GET_INVITATIONS, []);

  return { isLoading, invitations };
};

function InvitationsService() {
  return { useGet };
}

export default InvitationsService;

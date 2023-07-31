import React, { useCallback, useEffect } from "react";
import CircularProgress from "@mui/material/CircularProgress";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { getInvitation } from "api";
import { GET_INVITATION, UPDATE_INVITATION } from "api/restapi/actionTypes";
import AcceptInvitation from "components/AcceptInvitation";
import Backdrop from "components/Backdrop";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useInitialMount } from "hooks/useInitialMount";
import { useLastResult } from "hooks/useLastResult";
import { useShouldRenderLoader } from "hooks/useShouldRenderLoader";
import { getHomeUrl } from "urls";
import { getQueryParams } from "utils/network";

const AcceptInvitationContainer = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { inviteId } = getQueryParams();

  const { apiData: { invitation = {} } = {} } = useApiData(GET_INVITATION);
  const { lastResult: { status } = {} } = useLastResult(GET_INVITATION);

  const { isInitialMount, setIsInitialMount } = useInitialMount();
  const { isLoading: isGetInvitationLoading } = useApiState(GET_INVITATION);

  const isLoading = useShouldRenderLoader(isInitialMount, [isGetInvitationLoading]);
  const { isLoading: isUpdateInvitationLoading } = useApiState(UPDATE_INVITATION);

  useEffect(() => {
    if (isInitialMount) {
      setIsInitialMount(false);
    }
  }, [isInitialMount, setIsInitialMount]);

  useEffect(() => {
    dispatch(getInvitation(inviteId));
  }, [dispatch, inviteId]);

  const redirectToHome = useCallback(
    (organizationId) => {
      navigate(getHomeUrl(organizationId));
    },
    [navigate]
  );

  const onSuccessAccept = () => {
    const { organization_id: organizationId } = invitation;

    redirectToHome(organizationId);
  };

  const onSuccessDecline = () => redirectToHome();

  return isLoading ? (
    <Backdrop>
      <CircularProgress />
    </Backdrop>
  ) : (
    <AcceptInvitation
      invitation={invitation}
      sendState={status}
      isUpdateLoading={isUpdateInvitationLoading}
      onSuccessAccept={onSuccessAccept}
      onSuccessDecline={onSuccessDecline}
    />
  );
};

export default AcceptInvitationContainer;

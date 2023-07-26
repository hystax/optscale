import React, { useEffect } from "react";
import CircularProgress from "@mui/material/CircularProgress";
import { useDispatch } from "react-redux";
import { getInvitations } from "api";
import { GET_INVITATIONS, UPDATE_INVITATION } from "api/restapi/actionTypes";
import AcceptInvitations from "components/AcceptInvitations";
import Backdrop from "components/Backdrop";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useNewAuthorization } from "hooks/useNewAuthorization";

const AcceptInvitationsContainer = () => {
  const { isGetOrganizationsLoading, isGetInvitationsLoading, isCreateOrganizationLoading, activateScope } =
    useNewAuthorization();

  const { apiData: invitations } = useApiData(GET_INVITATIONS, []);
  const { isLoading: isUpdateInvitationLoading } = useApiState(UPDATE_INVITATION);

  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(getInvitations());
  }, [dispatch]);

  return isGetInvitationsLoading ? (
    <Backdrop>
      <CircularProgress />
    </Backdrop>
  ) : (
    <AcceptInvitations
      invitations={invitations}
      activateScope={activateScope}
      isLoadingProps={{
        isGetInvitationsLoading,
        isGetOrganizationsLoading,
        isCreateOrganizationLoading,
        isUpdateInvitationLoading
      }}
    />
  );
};

export default AcceptInvitationsContainer;

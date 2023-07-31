import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import { createInvitations, getAvailablePools } from "api";
import { CREATE_INVITATIONS, GET_AVAILABLE_POOLS } from "api/restapi/actionTypes";
import InviteEmployees from "components/InviteEmployees";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

const InviteEmployeesContainer = () => {
  const dispatch = useDispatch();

  const { isLoading: isCreateInvitationsLoading } = useApiState(CREATE_INVITATIONS);

  const { organizationId } = useOrganizationInfo();

  const { isLoading: isGetAvailablePoolsLoading, shouldInvoke } = useApiState(GET_AVAILABLE_POOLS, { organizationId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getAvailablePools(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  const {
    apiData: { pools = [] }
  } = useApiData(GET_AVAILABLE_POOLS);

  const onSubmit = (data, callback) =>
    dispatch((_, getState) => {
      dispatch(createInvitations(data)).then(() => {
        if (!isError(CREATE_INVITATIONS, getState())) {
          callback();
        }
      });
    });

  return (
    <InviteEmployees
      isLoadingProps={{ isGetAvailablePoolsLoading, isCreateInvitationsLoading }}
      onSubmit={onSubmit}
      availablePools={pools}
    />
  );
};

export default InviteEmployeesContainer;

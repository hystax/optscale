import { NetworkStatus } from "@apollo/client";
import { ORGANIZATION_SETUP_MODE } from "containers/InitializeContainer/constants";
import { useOrganizationsQuery } from "graphql/__generated__/hooks/restapi";
import { useGetToken } from "hooks/useGetToken";
import { isEmptyArray } from "utils/arrays";
import { getEnvironmentVariable } from "utils/env";
import { Error, Loading } from "../../common";
import ProceedToApplication from "../ProceedToApplication";
import SetupOrganization from "./SetupOrganization";
import ThanksForSigningUp from "./ThanksForSigningUp";

const StepContainer = ({ refetchInvitations, isInvitationsRefetching }) => {
  const { userEmail } = useGetToken();

  const {
    data: organizations,
    networkStatus: getOrganizationsNetworkStatus,
    error: getOrganizationsError,
    refetch: refetchOrganizations,
  } = useOrganizationsQuery({
    fetchPolicy: "no-cache",
    notifyOnNetworkStatusChange: true,
  });

  const getOrganizationsLoading = getOrganizationsNetworkStatus === NetworkStatus.loading;

  if (getOrganizationsLoading) {
    return <Loading />;
  }

  if (getOrganizationsError) {
    return <Error />;
  }

  const hasOrganizations = !isEmptyArray(organizations?.organizations ?? []);

  if (hasOrganizations) {
    return <ProceedToApplication />;
  }

  const organizationSetupMode = getEnvironmentVariable("VITE_ON_INITIALIZE_ORGANIZATION_SETUP_MODE");

  if (organizationSetupMode === ORGANIZATION_SETUP_MODE.INVITE_ONLY) {
    return <ThanksForSigningUp refetchInvitations={refetchInvitations} isInvitationsRefetching={isInvitationsRefetching} />;
  }

  return <SetupOrganization userEmail={userEmail} refetchOrganizations={refetchOrganizations} />;
};

export default StepContainer;

import { useState } from "react";
import { NetworkStatus } from "@apollo/client";
import { useInvitationsQuery } from "graphql/__generated__/hooks/restapi";
import { isEmptyArray } from "utils/arrays";
import { Error, Loading } from "../../common";
import SetupOrganization from "../SetupOrganization/StepContainer";
import AcceptInvitations from "./AcceptInvitations";

const StepContainer = () => {
  const [proceedToNext, setProceedToNext] = useState(false);

  const {
    data: invitations,
    networkStatus: getInvitationsNetworkStatus,
    error: getInvitationsError,
    refetch: refetchInvitations,
  } = useInvitationsQuery({
    fetchPolicy: "no-cache",
    notifyOnNetworkStatusChange: true,
  });

  const onRefetch = ({ onSuccess, onError } = {}) => {
    refetchInvitations()
      .then((queryResult) => {
        if (typeof onSuccess === "function") {
          onSuccess(queryResult);
        }
      })
      .catch((error) => {
        if (typeof onError === "function") {
          onError(error);
        }
      })
      .finally(() => {
        setProceedToNext(false);
      });
  };

  const getInvitationsLoading = getInvitationsNetworkStatus === NetworkStatus.loading;
  const getInvitationsRefetching = getInvitationsNetworkStatus === NetworkStatus.refetch;

  const error = getInvitationsError;

  if (getInvitationsLoading) {
    return <Loading />;
  }

  if (error) {
    return <Error />;
  }

  if (proceedToNext) {
    return <SetupOrganization isInvitationsRefetching={getInvitationsRefetching} refetchInvitations={onRefetch} />;
  }

  const hasInvitations = !isEmptyArray(invitations?.invitations ?? []);

  if (hasInvitations) {
    return (
      <AcceptInvitations
        invitations={invitations?.invitations ?? []}
        refetchInvitations={onRefetch}
        onProceed={() => {
          setProceedToNext(true);
        }}
      />
    );
  }

  return <SetupOrganization isInvitationsRefetching={getInvitationsRefetching} refetchInvitations={onRefetch} />;
};

export default StepContainer;

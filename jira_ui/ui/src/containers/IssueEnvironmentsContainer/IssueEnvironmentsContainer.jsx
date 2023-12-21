import React, { useCallback, useEffect, useState } from "react";
import IssueEnvironments from "components/IssueEnvironments";
import SpinnerLoader from "components/SpinnerLoader";
import {
  getIsUserConnectedToOptscale,
  getIsOrganizationAssigned,
  getCurrentIssueEnvironments,
  getAllEnvironments,
  getCurrentIssueInfo
} from "utils/api";

const excludeCurrentIssueStatusFromAvailable = (currentStatus, availableStatuses) =>
  availableStatuses.filter((availableStatus) => availableStatus !== currentStatus);

const IssueEnvironmentsContainer = () => {
  const [isInitialRequestsLoaded, setIsInitialRequestsLoaded] = useState(false);
  const [isRefetchingEnvironments, setIsRefetchingEnvironments] = useState(false);

  const [error, setError] = useState(false);

  const [isUserConnected, setIsUserConnected] = useState();
  const [isOrganizationAssigned, setIsOrganizationAssigned] = useState();
  const [currentIssueEnvironments, setCurrentIssueEnvironments] = useState();
  const [allEnvironments, setAllEnvironments] = useState();
  const [availableIssueStatusesForAutomaticUnlinking, setavailableIssueStatusesForAutomaticUnlinking] = useState([]);

  const makeInitialRequests = useCallback(async () => {
    setIsInitialRequestsLoaded(false);
    try {
      const [{ isConnected: isConnectedApiData }, { isOrganizationAssigned: isOrganizationAssignedApiData }] =
        await Promise.all([getIsUserConnectedToOptscale(), getIsOrganizationAssigned()]);
      setIsUserConnected(isConnectedApiData);
      setIsOrganizationAssigned(isOrganizationAssignedApiData);

      if (isOrganizationAssignedApiData) {
        const [currentIssueEnvironmentsApiData, allEnvironmentsApiData, issueInfoApiData] = await Promise.all([
          getCurrentIssueEnvironments(),
          getAllEnvironments(),
          getCurrentIssueInfo()
        ]);
        setCurrentIssueEnvironments(currentIssueEnvironmentsApiData);
        setAllEnvironments(allEnvironmentsApiData);
        setavailableIssueStatusesForAutomaticUnlinking(
          excludeCurrentIssueStatusFromAvailable(issueInfoApiData.current_status, issueInfoApiData.available_statuses)
        );
      }
    } catch {
      setError(true);
    } finally {
      setIsInitialRequestsLoaded(true);
    }
  }, []);

  const refetchEnvironments = async () => {
    setIsRefetchingEnvironments(true);
    try {
      const [currentIssueEnvironmentsApiData, allEnvironmentsApiData] = await Promise.all([
        getCurrentIssueEnvironments(),
        getAllEnvironments()
      ]);
      setCurrentIssueEnvironments(currentIssueEnvironmentsApiData);
      setAllEnvironments(allEnvironmentsApiData);
    } catch {
      setError(true);
    } finally {
      setIsRefetchingEnvironments(false);
    }
  };

  useEffect(() => {
    makeInitialRequests();
  }, [makeInitialRequests]);

  if (!isInitialRequestsLoaded || isRefetchingEnvironments) {
    return <SpinnerLoader />;
  }
  if (error) {
    return "Something went wrong :(";
  }

  return (
    <IssueEnvironments
      environmentsAttachedToCurrentIssue={currentIssueEnvironments?.shareable_resources ?? []}
      isUserConnected={isUserConnected}
      isOrganizationAssigned={isOrganizationAssigned}
      refetchEnvironments={refetchEnvironments}
      refetchInitialRequests={makeInitialRequests}
      allEnvironments={allEnvironments}
      availableIssueStatusesForAutomaticUnlinking={availableIssueStatusesForAutomaticUnlinking}
    />
  );
};

export default IssueEnvironmentsContainer;

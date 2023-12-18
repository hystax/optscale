import React from "react";
import OrganizationAssignmentSelector from "components/OrganizationAssignmentSelector";
import SpinnerLoader from "components/SpinnerLoader";
import { useGet } from "hooks/useGet";
import { useIsAdminister } from "hooks/useIsAdminister";
import { useUpdateOrganizationAssignment } from "hooks/useUpdateOrganizationAssignment";
import { isEmpty as isEmptyArray } from "utils/arrays";

const useGetOrganizationAssignment = () => {
  const { loading, error, data } = useGet("/jira_bus/v2/organization_assignment?details=true");

  const organizationIsNotAssigned = error?.error_code === "OJ0019";

  return {
    loading,
    error: organizationIsNotAssigned ? null : error,
    data
  };
};

const OrganizationAssignmentContainer = () => {
  const {
    loading: getOrganizationsLoading,
    error: getOrganizationsError,
    data: organizationsData
  } = useGet("/jira_bus/v2/organization");

  const {
    loading: getOrganizationAssignmentLoading,
    error: getOrganizationAssignmentError,
    data: organizationAssignmentData
  } = useGetOrganizationAssignment();

  const { loading: setOrganizationAssignmentLoading, onSubmit } = useUpdateOrganizationAssignment();

  const {
    loading: getAdministerPermissionLoading,
    error: getAdministerPermissionError,
    data: administerPermissionData
  } = useIsAdminister();

  if (getOrganizationsLoading || getOrganizationAssignmentLoading || getAdministerPermissionLoading) {
    return <SpinnerLoader height="50px" />;
  }

  if (getOrganizationsError || getOrganizationAssignmentError || getAdministerPermissionError) {
    return "Something went wrong :(";
  }

  const organizationsWhereUserIsManager =
    organizationsData?.organizations.filter(({ is_manager: isManager }) => isManager) ?? [];

  return !isEmptyArray(organizationsWhereUserIsManager) && administerPermissionData?.isAdministrator ? (
    <OrganizationAssignmentSelector
      onChange={({ id }) => onSubmit(id)}
      isLoading={setOrganizationAssignmentLoading}
      defaultValue={organizationsWhereUserIsManager.find(({ id }) => organizationAssignmentData?.organization_id === id)}
      options={organizationsWhereUserIsManager}
    />
  ) : (
    "You are not allowed to assign an Organization."
  );
};

OrganizationAssignmentContainer.propTypes = {};

export default OrganizationAssignmentContainer;

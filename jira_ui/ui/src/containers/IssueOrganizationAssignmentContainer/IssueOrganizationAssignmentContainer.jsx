import React from "react";
import SpinnerLoader from "components/SpinnerLoader";
import { useIsAdminister } from "hooks/useIsAdminister";

const IssueOrganizationAssignmentContainer = () => {
  const { loading: getAdministerPermissionLoading, data: administerPermissionData } = useIsAdminister();

  const renderWhatToDoMessage = () => (
    <p>
      {administerPermissionData?.isAdministrator
        ? "Go to application settings to assign an OptScale organization"
        : "Contact your Jira administrator to assign an OptScale organization"}
    </p>
  );

  return (
    <div>
      <p>OptScale organization is not assigned</p>
      {getAdministerPermissionLoading ? <SpinnerLoader height="50px" size={25} /> : renderWhatToDoMessage()}
    </div>
  );
};

export default IssueOrganizationAssignmentContainer;

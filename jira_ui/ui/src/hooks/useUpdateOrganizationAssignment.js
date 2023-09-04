import { useState } from "react";
import makeRequest from "utils/makeRequest";

export const useUpdateOrganizationAssignment = () => {
  const [setOrganizationAssignmentLoading, setSetOrganizationAssignmentLoading] = useState(false);

  const onSubmit = (organizationId) => {
    setSetOrganizationAssignmentLoading(true);

    makeRequest({
      url: "/jira_bus/v2/organization_assignment",
      options: {
        method: "POST",
        body: JSON.stringify({
          organization_id: organizationId
        })
      }
    }).finally(() => {
      setSetOrganizationAssignmentLoading(false);
    });
  };

  return {
    onSubmit,
    loading: setOrganizationAssignmentLoading
  };
};

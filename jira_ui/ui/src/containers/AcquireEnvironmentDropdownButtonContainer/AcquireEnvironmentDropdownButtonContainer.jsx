import React, { useState } from "react";
import PropTypes from "prop-types";
import { AcquireEnvironmentDropdownButton } from "components/EnvironmentAttachmentDropdownButtons";
import makeRequest from "utils/makeRequest";

const AcquireEnvironmentDropdownButtonContainer = ({
  environmentId,
  onSuccess,
  availableIssueStatusesForAutomaticUnlinking,
  tableRef,
  setMarginToFitDropdownMenu
}) => {
  const [isLoading, setIsLoading] = useState(false);

  const onAttach = ({ detachOnIssueStatus, releaseEnvironmentIfNoIssueAttached }) => {
    setIsLoading(true);
    makeRequest({
      url: `/jira_bus/v2/shareable_resource/${environmentId}/shareable_book`,
      options: {
        method: "POST",
        body: JSON.stringify({
          jira_auto_release: releaseEnvironmentIfNoIssueAttached
        })
      }
    })
      .then(({ error }) => {
        if (error) {
          return Promise.reject(error);
        }

        return makeRequest({
          url: `/jira_bus/v2/shareable_resource/${environmentId}/issue_attachment`,
          options: {
            method: "POST",
            body: JSON.stringify({
              auto_detach_status: detachOnIssueStatus
            })
          }
        });
      })
      .then(({ error }) => {
        if (error) {
          return Promise.reject(error);
        }

        setIsLoading(false);

        if (!error && typeof onSuccess === "function") {
          onSuccess();
        }

        return Promise.resolve();
      })
      .catch(() => {
        setIsLoading(false);
      });
  };

  return (
    <AcquireEnvironmentDropdownButton
      onAttach={onAttach}
      isLoading={isLoading}
      availableIssueStatusesForAutomaticUnlinking={availableIssueStatusesForAutomaticUnlinking}
      tableRef={tableRef}
      setMarginToFitDropdownMenu={setMarginToFitDropdownMenu}
    />
  );
};

AcquireEnvironmentDropdownButtonContainer.propTypes = {
  environmentId: PropTypes.string.isRequired,
  onSuccess: PropTypes.func.isRequired,
  availableIssueStatusesForAutomaticUnlinking: PropTypes.array.isRequired,
  tableRef: PropTypes.oneOfType([PropTypes.func, PropTypes.shape({ current: PropTypes.instanceOf(Element) })]).isRequired,
  setMarginToFitDropdownMenu: PropTypes.func.isRequired
};

export default AcquireEnvironmentDropdownButtonContainer;

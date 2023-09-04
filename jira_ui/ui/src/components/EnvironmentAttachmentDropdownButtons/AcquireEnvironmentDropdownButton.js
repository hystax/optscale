import React from "react";
import PropTypes from "prop-types";
import { useAutoDetachOnStatus } from "hooks/useAutoDetachOnStatus";
import { useReleaseEnvironmentIfNoIssueAttached } from "hooks/useReleaseEnvironmentIfNoIssueAttached";
import DropdownApplyButton from "./DropdownApplyButton";
import DropdownButton from "./DropdownButton";

export const AcquireEnvironmentDropdownButton = ({
  onAttach,
  availableIssueStatusesForAutomaticUnlinking,
  isLoading = false
}) => {
  const { values: detachOnStatusValues, content: detachOnStatusContent } = useAutoDetachOnStatus(
    availableIssueStatusesForAutomaticUnlinking
  );

  const { values: releaseEnvironmentIfNoIssueAttachedValues, content: releaseEnvironmentIfNoIssueAttachedContent } =
    useReleaseEnvironmentIfNoIssueAttached();

  return (
    <DropdownButton trigger="Acquire" isLoading={isLoading}>
      {detachOnStatusContent}
      {releaseEnvironmentIfNoIssueAttachedContent}
      <hr />
      <DropdownApplyButton
        text="Acquire and link this issue"
        onClick={() =>
          onAttach({
            ...detachOnStatusValues,
            ...releaseEnvironmentIfNoIssueAttachedValues
          })
        }
      />
    </DropdownButton>
  );
};

AcquireEnvironmentDropdownButton.propTypes = {
  onAttach: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  availableIssueStatusesForAutomaticUnlinking: PropTypes.array.isRequired
};

export default AcquireEnvironmentDropdownButton;

import React from "react";
import PropTypes from "prop-types";
import { useAutoDetachOnStatus } from "hooks/useAutoDetachOnStatus";
import DropdownApplyButton from "./DropdownApplyButton";
import DropdownButton from "./DropdownButton";

export const AttachEnvironmentDropdownButton = ({
  onAttach,
  availableIssueStatusesForAutomaticUnlinking,
  isLoading = false
}) => {
  const { values: detachOnStatusValues, content: detachOnStatusContent } = useAutoDetachOnStatus(
    availableIssueStatusesForAutomaticUnlinking
  );

  return (
    <DropdownButton trigger="Link" isLoading={isLoading}>
      {detachOnStatusContent}
      <DropdownApplyButton text="Link this issue" onClick={() => onAttach(detachOnStatusValues)} />
    </DropdownButton>
  );
};

AttachEnvironmentDropdownButton.propTypes = {
  onAttach: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  availableIssueStatusesForAutomaticUnlinking: PropTypes.array.isRequired
};

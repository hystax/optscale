import React from "react";
import { DropdownItemGroup } from "@atlaskit/dropdown-menu";
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
    <DropdownButton triggerLabel="Link" isLoading={isLoading}>
      {detachOnStatusContent}
      <DropdownItemGroup hasSeparator>
        <DropdownApplyButton text="Link this issue" onClick={() => onAttach(detachOnStatusValues)} />
      </DropdownItemGroup>
    </DropdownButton>
  );
};

AttachEnvironmentDropdownButton.propTypes = {
  onAttach: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  availableIssueStatusesForAutomaticUnlinking: PropTypes.array.isRequired
};

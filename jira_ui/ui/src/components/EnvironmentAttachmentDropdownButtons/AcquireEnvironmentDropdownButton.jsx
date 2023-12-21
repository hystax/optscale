import React from "react";
import { DropdownItemGroup } from "@atlaskit/dropdown-menu";
import PropTypes from "prop-types";
import { useAutoDetachOnStatus } from "hooks/useAutoDetachOnStatus";
import { useReleaseEnvironmentIfNoIssueAttached } from "hooks/useReleaseEnvironmentIfNoIssueAttached";
import DropdownApplyButton from "./DropdownApplyButton";
import DropdownButton from "./DropdownButton";

export const AcquireEnvironmentDropdownButton = ({
  onAttach,
  availableIssueStatusesForAutomaticUnlinking,
  isLoading = false,
  tableRef,
  setMarginToFitDropdownMenu
}) => {
  const { values: detachOnStatusValues, content: detachOnStatusContent } = useAutoDetachOnStatus(
    availableIssueStatusesForAutomaticUnlinking
  );

  const { values: releaseEnvironmentIfNoIssueAttachedValues, content: releaseEnvironmentIfNoIssueAttachedContent } =
    useReleaseEnvironmentIfNoIssueAttached();

  return (
    <DropdownButton
      triggerLabel="Acquire"
      isLoading={isLoading}
      tableRef={tableRef}
      setMarginToFitDropdownMenu={setMarginToFitDropdownMenu}
    >
      {detachOnStatusContent}
      {releaseEnvironmentIfNoIssueAttachedContent}
      <DropdownItemGroup hasSeparator>
        <DropdownApplyButton
          text="Acquire and link this issue"
          onClick={() =>
            onAttach({
              ...detachOnStatusValues,
              ...releaseEnvironmentIfNoIssueAttachedValues
            })
          }
        />
      </DropdownItemGroup>
    </DropdownButton>
  );
};

AcquireEnvironmentDropdownButton.propTypes = {
  onAttach: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  availableIssueStatusesForAutomaticUnlinking: PropTypes.array.isRequired,
  tableRef: PropTypes.oneOfType([PropTypes.func, PropTypes.shape({ current: PropTypes.instanceOf(Element) })]).isRequired,
  setMarginToFitDropdownMenu: PropTypes.func.isRequired
};

export default AcquireEnvironmentDropdownButton;

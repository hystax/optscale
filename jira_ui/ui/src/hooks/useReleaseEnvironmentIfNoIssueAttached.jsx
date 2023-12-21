import React, { useState } from "react";
import { DropdownItemCheckboxGroup, DropdownItemCheckbox, DropdownItemGroup } from "@atlaskit/dropdown-menu";

export const useReleaseEnvironmentIfNoIssueAttached = () => {
  const [releaseEnvironmentIfNoIssueAttached, setReleaseEnvironmentIfNoIssueAttached] = useState(true);

  const content = (
    <DropdownItemGroup hasSeparator>
      <DropdownItemCheckboxGroup id="releaseEnvironmentGroupCheckbox">
        <DropdownItemCheckbox
          id="releaseEnvironmentCheckbox"
          isSelected={releaseEnvironmentIfNoIssueAttached}
          onClick={() => setReleaseEnvironmentIfNoIssueAttached(!releaseEnvironmentIfNoIssueAttached)}
        >
          <div style={{ whiteSpace: "normal" }}>Release environment if no issues linked</div>
        </DropdownItemCheckbox>
      </DropdownItemCheckboxGroup>
    </DropdownItemGroup>
  );

  return {
    values: {
      releaseEnvironmentIfNoIssueAttached
    },
    content
  };
};

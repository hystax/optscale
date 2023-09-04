import React, { useState } from "react";
import { DropdownItemGroupCheckbox, DropdownItemCheckbox } from "@atlaskit/dropdown-menu";

export const useReleaseEnvironmentIfNoIssueAttached = () => {
  const [releaseEnvironmentIfNoIssueAttached, setReleaseEnvironmentIfNoIssueAttached] = useState(true);

  const content = (
    <DropdownItemGroupCheckbox id="releaseEnvironmentGroupCheckbox">
      <DropdownItemCheckbox
        id="releaseEnvironmentCheckbox"
        isSelected={releaseEnvironmentIfNoIssueAttached}
        onClick={() => setReleaseEnvironmentIfNoIssueAttached(!releaseEnvironmentIfNoIssueAttached)}
      >
        <div style={{ whiteSpace: "normal" }}>Release environment if no issues linked</div>
      </DropdownItemCheckbox>
    </DropdownItemGroupCheckbox>
  );

  return {
    values: {
      releaseEnvironmentIfNoIssueAttached
    },
    content
  };
};

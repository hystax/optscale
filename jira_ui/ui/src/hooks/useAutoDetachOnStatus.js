import React, { useState } from "react";
import {
  DropdownItemGroupCheckbox,
  DropdownItemCheckbox,
  DropdownItemGroupRadio,
  DropdownItemRadio
} from "@atlaskit/dropdown-menu";

export const useAutoDetachOnStatus = (availableIssueStatuses) => {
  const [autoDetachOnStatus, setAutoDetachOnStatus] = useState(false);
  const [detachOnIssueStatus, setDetachOnIssueStatus] = useState(availableIssueStatuses[0]);

  const content =
    availableIssueStatuses.length > 0 ? (
      <>
        <DropdownItemGroupCheckbox id="detachOnStatusGroupCheckbox">
          <DropdownItemCheckbox
            id="detachOnStatusCheckbox"
            isSelected={autoDetachOnStatus}
            onClick={() => setAutoDetachOnStatus(!autoDetachOnStatus)}
          >
            Auto unlink on status
          </DropdownItemCheckbox>
        </DropdownItemGroupCheckbox>
        {autoDetachOnStatus && (
          <DropdownItemGroupRadio id="issueStatusesRadioGroup">
            {availableIssueStatuses.map((status) => (
              <DropdownItemRadio
                isSelected={status === detachOnIssueStatus}
                id={status}
                onClick={() => setDetachOnIssueStatus(status)}
                key={status}
              >
                {status}
              </DropdownItemRadio>
            ))}
          </DropdownItemGroupRadio>
        )}
        <hr />
      </>
    ) : null;

  return {
    values: {
      detachOnIssueStatus: autoDetachOnStatus ? detachOnIssueStatus : undefined
    },
    content
  };
};

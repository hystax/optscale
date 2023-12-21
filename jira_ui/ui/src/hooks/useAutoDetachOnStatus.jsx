import React, { useState } from "react";
import {
  DropdownItemCheckboxGroup,
  DropdownItemCheckbox,
  DropdownItemRadioGroup,
  DropdownItemRadio,
  DropdownItemGroup
} from "@atlaskit/dropdown-menu";

export const useAutoDetachOnStatus = (availableIssueStatuses) => {
  const [autoDetachOnStatus, setAutoDetachOnStatus] = useState(false);
  const [detachOnIssueStatus, setDetachOnIssueStatus] = useState(availableIssueStatuses[0]);

  const content =
    availableIssueStatuses.length > 0 ? (
      <DropdownItemGroup hasSeparator>
        <DropdownItemCheckboxGroup id="detachOnStatusGroupCheckbox">
          <DropdownItemCheckbox
            id="detachOnStatusCheckbox"
            isSelected={autoDetachOnStatus}
            onClick={() => setAutoDetachOnStatus(!autoDetachOnStatus)}
          >
            Auto unlink on status
          </DropdownItemCheckbox>
        </DropdownItemCheckboxGroup>
        {autoDetachOnStatus && (
          <DropdownItemRadioGroup id="issueStatusesRadioGroup">
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
          </DropdownItemRadioGroup>
        )}
      </DropdownItemGroup>
    ) : null;

  return {
    values: {
      detachOnIssueStatus: autoDetachOnStatus ? detachOnIssueStatus : undefined
    },
    content
  };
};

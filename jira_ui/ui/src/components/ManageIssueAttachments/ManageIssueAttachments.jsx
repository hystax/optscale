import React, { useState } from "react";
import Button from "@atlaskit/button";
import PropTypes from "prop-types";
import AttachAnotherEnvironment from "components/AttachAnotherEnvironment";
import IssueAttachmentsDetails from "components/IssueAttachmentsDetails";
import IssueIsNotAttachedToEnvironment from "components/IssueIsNotAttachedToEnvironment";

const ManageIssueAttachments = ({
  attachedEnvironments,
  myEnvironments,
  availableEnvironments,
  otherEnvironments,
  availableIssueStatusesForAutomaticUnlinking,
  onSuccessAttachment,
  onSuccessDetachEnvironment,
  onSuccessReleaseEnvironment
}) => {
  const [isAcquireModeActive, setIsAcquireModeActive] = useState(false);

  if (attachedEnvironments.length === 0) {
    return (
      <div>
        <IssueIsNotAttachedToEnvironment />
        <AttachAnotherEnvironment
          myEnvironments={myEnvironments}
          availableEnvironments={availableEnvironments}
          otherEnvironments={otherEnvironments}
          availableIssueStatusesForAutomaticUnlinking={availableIssueStatusesForAutomaticUnlinking}
          onSuccessAttachment={onSuccessAttachment}
        />
      </div>
    );
  }

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "flex-end"
        }}
      >
        <Button
          appearance="link"
          onClick={() => {
            setIsAcquireModeActive(!isAcquireModeActive);
          }}
        >
          {isAcquireModeActive ? "See linked environments" : "Acquire another environment"}
        </Button>
      </div>
      {isAcquireModeActive ? (
        <AttachAnotherEnvironment
          myEnvironments={myEnvironments}
          availableEnvironments={availableEnvironments}
          otherEnvironments={otherEnvironments}
          onSuccessAttachment={() => onSuccessAttachment()}
          availableIssueStatusesForAutomaticUnlinking={availableIssueStatusesForAutomaticUnlinking}
        />
      ) : (
        <IssueAttachmentsDetails
          isAllowedToManageAttachments
          onSuccessDetachEnvironment={onSuccessDetachEnvironment}
          onSuccessReleaseEnvironment={onSuccessReleaseEnvironment}
          attachedEnvironments={attachedEnvironments}
        />
      )}
    </div>
  );
};

ManageIssueAttachments.propTypes = {
  attachedEnvironments: PropTypes.array.isRequired,
  onSuccessAttachment: PropTypes.func.isRequired,
  onSuccessDetachEnvironment: PropTypes.func.isRequired,
  onSuccessReleaseEnvironment: PropTypes.func.isRequired,
  availableIssueStatusesForAutomaticUnlinking: PropTypes.array.isRequired,
  myEnvironments: PropTypes.array.isRequired,
  availableEnvironments: PropTypes.array.isRequired,
  otherEnvironments: PropTypes.array.isRequired
};

export default ManageIssueAttachments;

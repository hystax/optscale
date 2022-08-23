import React from "react";
import PropTypes from "prop-types";
import IssueAttachmentsDetails from "components/IssueAttachmentsDetails";
import IssueIsNotAttachedToEnvironment from "components/IssueIsNotAttachedToEnvironment";
import ManageIssueAttachments from "components/ManageIssueAttachments";
import IssueOrganizationAssignmentContainer from "containers/IssueOrganizationAssignmentContainer";
import LoginToOptscaleButtonContainer from "containers/LoginToOptscaleButtonContainer";

const excludeAttachedEnvironments = (environments, environmentsAttachedToCurrentIssue) => {
  const attachedEnvironmentIds = environmentsAttachedToCurrentIssue.map(({ id }) => id);
  return environments.filter(({ id }) => !attachedEnvironmentIds.includes(id));
};

const isMyEnvironment = (environment) =>
  environment?.book_permission === "allowed" && environment?.current_booking?.acquired_by_me;

const isAvailableEnvironment = (environment) => environment?.book_permission === "allowed" && !environment?.current_booking;

const splitEnvironments = (environments) =>
  environments.reduce(
    (groupedEnvironments, environment) => {
      if (isMyEnvironment(environment)) {
        return {
          ...groupedEnvironments,
          myEnvironments: [...groupedEnvironments.myEnvironments, environment]
        };
      }
      if (isAvailableEnvironment(environment)) {
        return {
          ...groupedEnvironments,
          availableEnvironments: [...groupedEnvironments.availableEnvironments, environment]
        };
      }
      return {
        ...groupedEnvironments,
        otherEnvironments: [...groupedEnvironments.otherEnvironments, environment]
      };
    },
    { myEnvironments: [], availableEnvironments: [], otherEnvironments: [] }
  );

const IssueEnvironments = ({
  environmentsAttachedToCurrentIssue,
  isUserConnected,
  isOrganizationAssigned,
  refetchEnvironments,
  allEnvironments,
  availableIssueStatusesForAutomaticUnlinking,
  refetchInitialRequests
}) => {
  if (isUserConnected) {
    if (!isOrganizationAssigned) {
      return <IssueOrganizationAssignmentContainer />;
    }

    const onSuccessChangingAttachmentStatus = () => {
      refetchEnvironments();
    };

    const { myEnvironments, availableEnvironments, otherEnvironments } = splitEnvironments(
      excludeAttachedEnvironments(allEnvironments?.shareable_resources ?? [], environmentsAttachedToCurrentIssue)
    );

    return (
      <ManageIssueAttachments
        myEnvironments={myEnvironments}
        availableEnvironments={availableEnvironments}
        otherEnvironments={otherEnvironments}
        availableIssueStatusesForAutomaticUnlinking={availableIssueStatusesForAutomaticUnlinking}
        attachedEnvironments={environmentsAttachedToCurrentIssue}
        onSuccessReleaseEnvironment={onSuccessChangingAttachmentStatus}
        onSuccessDetachEnvironment={onSuccessChangingAttachmentStatus}
        onSuccessAttachment={onSuccessChangingAttachmentStatus}
      />
    );
  }

  const noAttachedEnvironments = environmentsAttachedToCurrentIssue.length === 0;

  const renderAttachmentDetails = () =>
    noAttachedEnvironments ? (
      <IssueIsNotAttachedToEnvironment />
    ) : (
      <IssueAttachmentsDetails attachedEnvironments={environmentsAttachedToCurrentIssue} />
    );

  return (
    <div>
      <div style={{ textAlign: "center", padding: "16px 0px" }}>
        <p style={{ marginBottom: "16px" }}>Connect your OptScale user to attach issues to Environments</p>
        <LoginToOptscaleButtonContainer onSuccess={refetchInitialRequests} />
      </div>
      {isOrganizationAssigned && renderAttachmentDetails()}
    </div>
  );
};

IssueEnvironments.propTypes = {
  environmentsAttachedToCurrentIssue: PropTypes.array,
  isUserConnected: PropTypes.bool,
  isOrganizationAssigned: PropTypes.bool,
  refetchEnvironments: PropTypes.func,
  allEnvironments: PropTypes.object,
  availableIssueStatusesForAutomaticUnlinking: PropTypes.array,
  refetchInitialRequests: PropTypes.func
};

export default IssueEnvironments;

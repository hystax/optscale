import React, { useState } from "react";
import { LoadingButton } from "@atlaskit/button";
import UnlinkIcon from "@atlaskit/icon/glyph/unlink";
import PropTypes from "prop-types";
import makeRequest from "utils/makeRequest";

const DetachIssueButtonContainer = ({ activeBooking, onSuccess }) => {
  const [isLoading, setIsLoading] = useState(false);

  const onClick = async () => {
    setIsLoading(true);

    const {
      jira: {
        issue: { key: issueKey }
      }
    } = await window.AP.context.getContext();

    const issueAssignment = activeBooking?.jira_issue_attachments.find(
      ({ issue_number: issueNumber, project_key: projectKey }) => `${projectKey}-${issueNumber}` === issueKey
    );

    if (issueAssignment) {
      makeRequest({
        url: `/jira_bus/v2/issue_attachment/${issueAssignment.id}`,
        options: { method: "DELETE" }
      }).then(({ error }) => {
        setIsLoading(false);
        if (!error && typeof onSuccess === "function") {
          onSuccess();
        }
      });
    } else {
      console.error("Unable to find issue attachment");
      setIsLoading(false);
    }
  };

  return (
    <LoadingButton iconBefore={<UnlinkIcon label="Detach icon" />} onClick={onClick} isLoading={isLoading}>
      Unlink this issue
    </LoadingButton>
  );
};

DetachIssueButtonContainer.propTypes = {
  activeBooking: PropTypes.object.isRequired,
  onSuccess: PropTypes.func.isRequired
};

export default DetachIssueButtonContainer;

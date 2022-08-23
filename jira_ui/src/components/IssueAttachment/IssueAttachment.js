import React from "react";
import LinkIcon from "@atlaskit/icon/glyph/question-circle";
import Lozenge from "@atlaskit/lozenge";
import Tooltip from "@atlaskit/tooltip";
import PropTypes from "prop-types";
import LinkToEnvironmentDetails from "components/LinkToEnvironmentDetails";
import Markdown from "components/Markdown";
import DetachIssueButtonContainer from "containers/DetachIssueButtonContainer";
import ReleaseEnvironmentButtonContainer from "containers/ReleaseEnvironmentButtonContainer";

const getJiraLinkMarkdown = ({ project_key: projectKey, issue_number: issueNumber, issue_link: issueLink }) => {
  const name = `${projectKey}-${issueNumber}`;

  return `[${name}](${issueLink})`;
};

const DetailsItem = ({ name, value }) => (
  <div
    style={{
      padding: "4px 0px",
      display: "grid",
      gridTemplateColumns: "110px 1fr"
    }}
  >
    <div>{name}</div>
    <div>{value}</div>
  </div>
);

const IssueAttachment = ({
  environment,
  isAllowedToManageAttachment = false,
  onSuccessDetachEnvironment,
  onSuccessReleaseEnvironment
}) => {
  const { details: environmentDetails, current_booking: currentBooking } = environment;
  const { details: activeBooking } = currentBooking ?? {};

  return (
    <div>
      <DetailsItem name="Environment" value={<LinkToEnvironmentDetails environment={environment} />} />
      <DetailsItem name="Type" value={environmentDetails.resource_type} />
      {activeBooking && (
        <>
          <DetailsItem
            name="Jira issues"
            value={<Markdown>{activeBooking.jira_issue_attachments.map(getJiraLinkMarkdown).join("\n")}</Markdown>}
          />
          <DetailsItem
            name={
              <div style={{ display: "flex" }}>
                <div style={{ marginRight: "4px" }}>Auto release</div>
                <Tooltip content="Auto release if no linked issues left">
                  <LinkIcon size="small" label="Question mark" />
                </Tooltip>
              </div>
            }
            value={
              activeBooking.jira_auto_release ? <Lozenge appearance="success">Enabled</Lozenge> : <Lozenge>Disabled</Lozenge>
            }
          />
        </>
      )}
      {isAllowedToManageAttachment && (
        <DetailsItem
          name="Actions"
          value={
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, 200px)",
                gap: "8px"
              }}
            >
              <DetachIssueButtonContainer activeBooking={activeBooking} onSuccess={onSuccessDetachEnvironment} />
              <ReleaseEnvironmentButtonContainer activeBooking={activeBooking} onSuccess={onSuccessReleaseEnvironment} />
            </div>
          }
        />
      )}
      {environmentDetails.env_properties &&
        Object.entries(environmentDetails.env_properties).map(([propertyKey, propertyValue]) => (
          <DetailsItem key={propertyKey} name={propertyKey} value={<Markdown>{propertyValue}</Markdown>} />
        ))}
    </div>
  );
};

IssueAttachment.propTypes = {
  environment: PropTypes.object.isRequired,
  isAllowedToManageAttachment: PropTypes.bool,
  onSuccessDetachEnvironment: PropTypes.func,
  onSuccessReleaseEnvironment: PropTypes.func
};

export default IssueAttachment;

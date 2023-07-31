import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ButtonLoader from "components/ButtonLoader";
import TextBlock from "components/TextBlock";
import JiraIcon from "icons/JiraIcon";
import { JIRA_MARKETPLACE } from "urls";
import { isEmpty } from "utils/arrays";
import Integration from "../Integration";
import Title from "../Title";

export const JIRA = "jira";

const Jira = ({
  totalEmployees,
  connectedEmployees,
  connectedWorkspaces,
  isCurrentEmployeeConnectedToJira,
  isLoadingProps = {}
}) => {
  const { isGetEmployeesLoading = false, isGetJiraOrganizationStatusLoading = false } = isLoadingProps;

  return (
    <Integration
      id={JIRA}
      title={<Title icon={<JiraIcon />} label={<FormattedMessage id="jira" />} />}
      button={
        <ButtonLoader
          messageId="getOptScaleJiraApp"
          isLoading={isGetJiraOrganizationStatusLoading}
          startIcon={<JiraIcon />}
          color="primary"
          href={JIRA_MARKETPLACE}
        />
      }
      blocks={[
        <TextBlock key="description1" messageId="integrationsJiraDescription1" />,
        <TextBlock
          key="jiraConnected"
          messageId="integrationsJiraConnected"
          isVisible={isCurrentEmployeeConnectedToJira}
          color="success"
        />,
        <TextBlock
          key="description2"
          messageId="integrationsJiraDescription2"
          isLoading={isGetEmployeesLoading}
          values={{
            total: totalEmployees,
            connected: connectedEmployees,
            strong: (chunks) => <strong>{chunks}</strong>
          }}
        />,
        <TextBlock
          key="noJiraWorkspacesConnected"
          messageId="noJiraWorkspacesAreConnected"
          isLoading={isGetJiraOrganizationStatusLoading}
          color="error"
          isVisible={isEmpty(connectedWorkspaces)}
        />,
        <TextBlock
          key="connectedWorkspacesTitle"
          messageId="connectedWorkspaces"
          isLoading={isGetJiraOrganizationStatusLoading}
          isVisible={!isEmpty(connectedWorkspaces)}
        />,
        !isGetJiraOrganizationStatusLoading && (
          <ul key="connectedWorkspaces" style={{ marginTop: 0 }}>
            {connectedWorkspaces.map(({ display_url: url }) => (
              <li key={url}>{url}</li>
            ))}
          </ul>
        )
      ]}
    />
  );
};

Jira.propTypes = {
  totalEmployees: PropTypes.number.isRequired,
  connectedEmployees: PropTypes.number.isRequired,
  connectedWorkspaces: PropTypes.array.isRequired,
  isCurrentEmployeeConnectedToJira: PropTypes.bool,
  isLoadingProps: PropTypes.shape({
    isGetEmployeesLoading: PropTypes.bool,
    isGetJiraOrganizationStatusLoading: PropTypes.bool
  })
};

export default Jira;

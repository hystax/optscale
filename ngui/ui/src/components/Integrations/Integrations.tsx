import Grid from "@mui/material/Grid";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import IntegrationJiraContainer from "containers/IntegrationJiraContainer";
import IntegrationsBIExportContainer from "containers/IntegrationsBIExportContainer";
import IntegrationsGoogleCalendarContainer from "containers/IntegrationsGoogleCalendarContainer";
import IntegrationsSlackContainer from "containers/IntegrationsSlackContainer";
import { getSquareNodesStyle } from "utils/layouts";
import { BI_EXPORT } from "./BIExport";
import GitHub from "./GitHub";
import { GITHUB } from "./GitHub/GitHub";
import GitLab from "./GitLab";
import { GITLAB } from "./GitLab/GitLab";
import { GOOGLE_CALENDAR } from "./GoogleCalendar/GoogleCalendar";
import Jenkins from "./Jenkins";
import { JENKINS } from "./Jenkins/Jenkins";
import { JIRA } from "./Jira/Jira";
import { SLACK_INTEGRATION } from "./Slack/Slack";

const actionBarDefinition = {
  title: {
    messageId: "integrations"
  }
};

const integrationsGridItems = [
  {
    node: <IntegrationsSlackContainer />,
    key: SLACK_INTEGRATION
  },
  {
    node: <IntegrationsGoogleCalendarContainer />,
    key: GOOGLE_CALENDAR
  },
  {
    node: <IntegrationJiraContainer />,
    key: JIRA
  },
  {
    node: <IntegrationsBIExportContainer />,
    key: BI_EXPORT
  },
  {
    node: <GitLab />,
    key: GITLAB
  },
  {
    node: <GitHub />,
    key: GITHUB
  },
  {
    node: <Jenkins />,
    key: JENKINS
  }
];

const Integrations = () => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <Grid container>
        {integrationsGridItems.map(({ key, node }, i) => (
          <Grid key={key} item md={12} lg={6} sx={getSquareNodesStyle(integrationsGridItems.length, i)}>
            {node}
          </Grid>
        ))}
      </Grid>
    </PageContentWrapper>
  </>
);

export default Integrations;

import React from "react";
import Grid from "@mui/material/Grid";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import IntegrationJiraContainer from "containers/IntegrationJiraContainer";
import IntegrationsGoogleCalendarContainer from "containers/IntegrationsGoogleCalendarContainer";
import IntegrationsSlackContainer from "containers/IntegrationsSlackContainer";
import { useInnerBorders } from "hooks/useInnerBorders";
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

const Integrations = () => {
  const makeBorders = useInnerBorders({
    tileCount: integrationsGridItems.length,
    columns: 2,
    borderStyle: "1px solid",
    lastChildBorderOnMobile: false
  });

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Grid container>
          {integrationsGridItems.map(({ key, node }, i) => (
            <Grid
              key={key}
              item
              xs={12}
              sm={6}
              sx={{
                ...makeBorders(i),
                borderColor: "divider"
              }}
            >
              {node}
            </Grid>
          ))}
        </Grid>
      </PageContentWrapper>
    </>
  );
};

export default Integrations;

import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import github from "assets/integrations/github.svg";
import gitlab from "assets/integrations/gitlab.svg";
import jenkins from "assets/integrations/jenkins.svg";
import jira from "assets/integrations/jira.svg";
import slack from "assets/integrations/slack.svg";
import terraform from "assets/integrations/terraform.svg";
import SubTitle from "components/SubTitle";
import useStyles from "./IntegrationsGallery.styles";

const integrationsLogos = [
  {
    src: slack,
    altMessageId: "slack"
  },
  {
    src: jenkins,
    altMessageId: "jenkins"
  },
  {
    src: jira,
    altMessageId: "jira"
  },
  {
    src: gitlab,
    altMessageId: "gitLab"
  },
  {
    src: github,
    altMessageId: "gitHub"
  },
  {
    src: terraform,
    altMessageId: "terraform"
  }
];

const IntegrationsGallery = () => {
  const intl = useIntl();
  const { classes } = useStyles();

  return (
    <div data-test-id="div_integrations">
      <SubTitle className={classes.title}>
        <FormattedMessage id="integrations" />
      </SubTitle>
      <div className={classes.logosWrapper}>
        {integrationsLogos.map((item) => (
          <div className={classes.logoWrapper} key={item.altMessageId}>
            <img src={item.src} alt={intl.formatMessage({ id: item.altMessageId })} className={classes.logoImage} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default IntegrationsGallery;

import { FormattedMessage, useIntl } from "react-intl";
import dataBricks from "assets/integrations/databricks.svg";
import github from "assets/integrations/github.svg";
import gitlab from "assets/integrations/gitlab.svg";
import jenkins from "assets/integrations/jenkins.svg";
import jira from "assets/integrations/jira.svg";
import kubeflow from "assets/integrations/kubeflow.svg";
import pytorch from "assets/integrations/pytorch.svg";
import slack from "assets/integrations/slack.svg";
import spark from "assets/integrations/spark.svg";
import tensorflow from "assets/integrations/tensorflow.svg";
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
  },
  {
    src: dataBricks,
    altMessageId: "databricks"
  },
  {
    src: pytorch,
    altMessageId: "pytorch"
  },
  {
    src: kubeflow,
    altMessageId: "kubeflow"
  },
  {
    src: spark,
    altMessageId: "spark"
  },
  {
    src: tensorflow,
    altMessageId: "tensorflow"
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

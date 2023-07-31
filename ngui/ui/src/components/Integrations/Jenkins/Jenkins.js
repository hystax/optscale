import React from "react";
import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CodeBlock from "components/CodeBlock";
import TextBlock from "components/TextBlock";
import JenkinsIcon from "icons/JenkinsIcon";
import { ENVIRONMENTS } from "urls";
import { ENV_COLLECTOR_URL } from "utils/constants";
import Integration from "../Integration";
import Title from "../Title";

export const JENKINS = "jenkins";

const JENKINS_CODE = `post {
  always {
      script {
         curl -X POST -d '{"Pipeline result": "$DEPLOY_RESULT", "Version": "$DEPLOY_COMMIT"}' $${ENV_COLLECTOR_URL}
      }
  }
}
`;

const Jenkins = () => (
  <Integration
    id={JENKINS}
    title={<Title icon={<JenkinsIcon />} label={<FormattedMessage id="jenkins" />} />}
    blocks={[
      <TextBlock
        key="description1"
        messageId="integrationsJenkinsDescription1"
        values={{
          link: (chunks) => (
            <Link to={ENVIRONMENTS} component={RouterLink}>
              {chunks}
            </Link>
          )
        }}
      />,
      <TextBlock key="description2" messageId="integrationsJenkinsDescription2" additionalCharactersAfterText=":" />,
      <CodeBlock key="code" text={JENKINS_CODE} />,
      <TextBlock
        key="description3"
        messageId="integrationsJenkinsDescription3"
        values={{
          strong: (chunks) => <strong>{chunks}</strong>
        }}
      />
    ]}
  />
);

export default Jenkins;

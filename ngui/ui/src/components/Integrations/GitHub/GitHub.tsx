import GitHubIcon from "@mui/icons-material/GitHub";
import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CodeBlock from "components/CodeBlock";
import TextBlock from "components/TextBlock";
import { ENVIRONMENTS } from "urls";
import { ENV_COLLECTOR_URL } from "utils/constants";
import Integration from "../Integration";
import Title from "../Title";

export const GITHUB = "gitHub";

const GITHUB_CODE = `- name: Send status
    if: always()
    run: curl -X POST -d '{"Pipeline result": "$DEPLOY_RESULT", "Version": "$DEPLOY_COMMIT"}' $${ENV_COLLECTOR_URL}
`;

const GitHub = () => (
  <Integration
    id={GITHUB}
    title={<Title icon={<GitHubIcon />} label={<FormattedMessage id="gitHub" />} />}
    blocks={[
      <TextBlock
        key="description1"
        messageId="integrationsGitHubDescription1"
        values={{
          link: (chunks) => (
            <Link to={ENVIRONMENTS} component={RouterLink}>
              {chunks}
            </Link>
          )
        }}
      />,
      <TextBlock key="description2" messageId="integrationsGitHubDescription2" additionalCharactersAfterText=":" />,
      <CodeBlock key="code" text={GITHUB_CODE} />,
      <TextBlock
        key="description3"
        messageId="integrationsGitHubDescription3"
        values={{
          strong: (chunks) => <strong>{chunks}</strong>
        }}
      />
    ]}
  />
);

export default GitHub;

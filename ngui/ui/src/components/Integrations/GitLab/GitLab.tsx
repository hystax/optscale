import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CodeBlock from "components/CodeBlock";
import TextBlock from "components/TextBlock";
import GitLabIcon from "icons/GitLabIcon";
import { ENVIRONMENTS } from "urls";
import { ENV_COLLECTOR_URL } from "utils/constants";
import Integration from "../Integration";
import Title from "../Title";

export const GITLAB = "gitLab";

const GITLAB_CODE = `stage: send_status
  needs: [$all_other_steps]
  if: always()
  script:
    - curl -X POST -d '{"Pipeline result": "$DEPLOY_RESULT", "Version": "$DEPLOY_COMMIT"}' $${ENV_COLLECTOR_URL}
`;

const GitLab = () => (
  <Integration
    id={GITLAB}
    title={<Title icon={<GitLabIcon />} label={<FormattedMessage id="gitLab" />} />}
    blocks={[
      <TextBlock
        key="description1"
        messageId="integrationsGitLabDescription1"
        values={{
          link: (chunks) => (
            <Link to={ENVIRONMENTS} component={RouterLink}>
              {chunks}
            </Link>
          )
        }}
      />,
      <TextBlock key="description2" messageId="integrationsGitLabDescription2" additionalCharactersAfterText=":" />,
      <CodeBlock key="code" text={GITLAB_CODE} />,
      <TextBlock
        key="description3"
        messageId="integrationsGitLabDescription3"
        values={{
          strong: (chunks) => <strong>{chunks}</strong>
        }}
      />
    ]}
  />
);

export default GitLab;

import React from "react";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CodeBlock from "components/CodeBlock";
import CopyText from "components/CopyText";
import { INTEGRATIONS } from "urls";

const EnvironmentCiCdIntegration = ({ text }) => (
  <>
    <Box mb={2}>
      <Typography>
        <FormattedMessage id="propertiesOfEnvironmentCanBeSetDirectlyFromYourCiCdPipelines" />
      </Typography>
    </Box>
    <Box mb={2}>
      <Typography>
        <FormattedMessage id="youNeedToInsertFollowingPOSTRequest" />
        {":"}
      </Typography>
    </Box>
    <Box mb={2}>
      <CodeBlock text={`curl -X POST -d '{"<property_name>":"<value>"}' ${text}`} />
    </Box>
    <Box mb={2}>
      <Typography>
        <FormattedMessage
          id="requestBodyShouldContainPlainJSON"
          values={{
            break: <br />,
            strong: (chunks) => <strong>{chunks}</strong>
          }}
        />
      </Typography>
    </Box>
    <Box mb={2}>
      <Typography>
        <FormattedMessage
          id="checkIntegrationsPage"
          values={{
            link: (chunks) => (
              <Link to={INTEGRATIONS} component={RouterLink}>
                {chunks}
              </Link>
            )
          }}
        />
      </Typography>
    </Box>
    <Box mb={2}>
      <Typography>
        <FormattedMessage id="pleaseUseTheFollowingEnvCollectorUrl" />
        <strong>
          <CopyText variant="inherit" text={text}>
            {text}
          </CopyText>
        </strong>
      </Typography>
    </Box>
  </>
);

EnvironmentCiCdIntegration.protoTypes = {
  text: PropTypes.string.isRequired
};

export default EnvironmentCiCdIntegration;

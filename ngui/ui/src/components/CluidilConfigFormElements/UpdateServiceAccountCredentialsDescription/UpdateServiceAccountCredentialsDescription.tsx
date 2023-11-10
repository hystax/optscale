import { Alert, Link, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { DOCS_HYSTAX_OPTSCALE } from "urls";

const UpdateServiceAccountCredentialsDescription = () => (
  <Alert severity="info">
    <Typography>
      <FormattedMessage
        id="updateNebiusCredentialsDescription.credentialsDocumentationReference"
        values={{
          link: (chunks) => (
            <Link
              data-test-id="link_credentials_docs"
              // TODO: Replace with a link to a documentation
              href={DOCS_HYSTAX_OPTSCALE}
              target="_blank"
              rel="noopener"
            >
              {chunks}
            </Link>
          )
        }}
      />
    </Typography>
  </Alert>
);

export default UpdateServiceAccountCredentialsDescription;

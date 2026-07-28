import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link } from "react-router-dom";
import { intl } from "translations/react-intl-config";
import {
  DOCS_HYSTAX_AWS_LINKED_DISCOVER_RESOURCES,
  DOCS_HYSTAX_CONNECT_AWS_ROOT,
  DOCS_HYSTAX_MIGRATE_FROM_CUR_TO_DATA_EXPORTS_CUR_2_0
} from "urls";
import { SPACING_2 } from "utils/layouts";

const AwsDescription = ({ config, authenticationType }) => {
  const getAwsDescription = (config) => {
    if (authenticationType === "assumedRole") {
      if (config.linked) {
        return (
          <Typography sx={{ marginBottom: SPACING_2 }}>
            <FormattedMessage
              id="createAwsAssumedRoleLinkedDescription"
              values={{ action: intl.formatMessage({ id: "save" }) }}
            />
          </Typography>
        );
      }

      return (
        <Typography sx={{ marginBottom: SPACING_2 }}>
          <FormattedMessage id="createAwsAssumedRoleDescription" values={{ action: intl.formatMessage({ id: "save" }) }} />
        </Typography>
      );
    }

    if (config.linked) {
      return (
        <Typography gutterBottom>
          <FormattedMessage
            id="createAwsLinkedDocumentationReference3"
            values={{
              discoverResourcesLink: (chunks) => (
                <Link
                  data-test-id="link_iam_user"
                  href={DOCS_HYSTAX_AWS_LINKED_DISCOVER_RESOURCES}
                  target="_blank"
                  rel="noopener"
                >
                  {chunks}
                </Link>
              )
            }}
          />
        </Typography>
      );
    }

    return (
      <Typography gutterBottom component="div">
        <div>
          <FormattedMessage
            id="createAwsRootDocumentationReference"
            values={{
              link: (chunks) => (
                <Link data-test-id="link_guide" href={DOCS_HYSTAX_CONNECT_AWS_ROOT} target="_blank" rel="noopener">
                  {chunks}
                </Link>
              ),
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </div>
        <div>
          <FormattedMessage
            id="migrateToCur2.0"
            values={{
              link: (chunks) => (
                <Link
                  data-test-id="link_guide"
                  href={DOCS_HYSTAX_MIGRATE_FROM_CUR_TO_DATA_EXPORTS_CUR_2_0}
                  target="_blank"
                  rel="noopener"
                >
                  {chunks}
                </Link>
              ),
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </div>
      </Typography>
    );
  };

  return <>{getAwsDescription(config)}</>;
};

export default AwsDescription;

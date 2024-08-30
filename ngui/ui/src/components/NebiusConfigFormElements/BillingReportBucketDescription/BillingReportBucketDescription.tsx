import { Alert, Link, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { NEBIUS_GET_FOLDER_REPORT } from "urls";

const BillingReportBucketDescription = () => (
  <Alert severity="info">
    <Typography gutterBottom>
      <FormattedMessage id="createNebiusDescription.billingReportBucket" />
    </Typography>
    <Typography gutterBottom>
      <FormattedMessage
        id="createNebiusDescription.billingReportBucketPath"
        values={{
          i: (chunks) => <i>{chunks}</i>
        }}
      />
    </Typography>
    <Typography gutterBottom>
      <FormattedMessage
        id="createNebiusDescription.billingReportBucketDocumentationReference"
        values={{
          link: (chunks) => (
            <Link data-test-id="link_get_folder_report" href={NEBIUS_GET_FOLDER_REPORT} target="_blank" rel="noopener">
              {chunks}
            </Link>
          )
        }}
      />
    </Typography>
  </Alert>
);

export default BillingReportBucketDescription;

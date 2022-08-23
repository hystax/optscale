import React from "react";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import MailTo from "components/MailTo";
import { EMAIL_SUPPORT } from "urls";
import { SPACING_1 } from "utils/layouts";

const DataUnderProcessing = () => (
  <Grid container spacing={SPACING_1}>
    <Grid item xs={12}>
      <Typography>
        <FormattedMessage id="finOpsAssessment.dataUnderProcessingDescription" />
      </Typography>
      <Typography>
        <FormattedMessage
          id="finOpsAssessment.dataUnderProcessingPostDescription"
          values={{
            p: (chunks) => <p>{chunks}</p>,
            supportLink: (chunks) => <MailTo email={EMAIL_SUPPORT} text={chunks} />
          }}
        />
      </Typography>
    </Grid>
  </Grid>
);

export default DataUnderProcessing;

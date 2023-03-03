import React from "react";
import { Typography } from "@mui/material";
import Grid from "@mui/material/Grid";
import { FormattedMessage } from "react-intl";
import ActionBar from "components/ActionBar";
import ExecutorsPanel from "components/ExecutorsPanel";
import PageContentWrapper from "components/PageContentWrapper";
import { SPACING_2 } from "utils/layouts";

const actionBarDefinition = {
  title: {
    messageId: "mlExecutorsTitle",
    dataTestId: "lbl_ml_executors"
  }
};

const MlExecutors = () => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <Grid container spacing={SPACING_2}>
        <Grid item xs={12}>
          <Typography>
            <FormattedMessage id="mlExecutorsDescription" />
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <ExecutorsPanel />
        </Grid>
      </Grid>
    </PageContentWrapper>
  </>
);

export default MlExecutors;

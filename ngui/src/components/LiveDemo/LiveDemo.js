import React from "react";
import { Typography } from "@mui/material";
import CircularProgress from "@mui/material/CircularProgress";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ButtonLoader from "components/ButtonLoader";
import ConditionWrapper from "components/ConditionWrapper";
import GridContainerWithNegativeMarginCompensation from "components/GridContainerWithNegativeMarginCompensation";
import Logo from "components/Logo";
import PageTitle from "components/PageTitle";
import { SPACING_4 } from "utils/layouts";

const LiveDemo = ({ isLoading, retry, showRetry = false }) => (
  <GridContainerWithNegativeMarginCompensation spacing={SPACING_4} direction="column" alignItems="center">
    <Grid item xs={12}>
      <Logo width={200} dataTestId="img_logo" />
    </Grid>
    <ConditionWrapper
      condition={isLoading}
      conditionTemplate={
        <>
          <Grid item xs={12}>
            <PageTitle dataTestId="p_preparing_ld" align="center">
              <FormattedMessage id="preparingLiveDemoMessage" />
            </PageTitle>
            <Typography align="center" data-test-id="p_process_ld">
              <FormattedMessage
                id="usuallyTheProcessTakesLessThanSeconds"
                values={{
                  value: 10
                }}
              />
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <CircularProgress data-test-id="svg_loading" />
          </Grid>
        </>
      }
    >
      <ConditionWrapper
        condition={showRetry}
        conditionTemplate={
          <>
            <Grid item xs={12}>
              <PageTitle align="center">
                <FormattedMessage id="failedLiveDemoMessage" />
              </PageTitle>
            </Grid>
            <Grid item xs={12}>
              <ButtonLoader
                size="large"
                messageId="retry"
                color="primary"
                variant="contained"
                onClick={retry}
                isLoading={isLoading}
              />
            </Grid>
          </>
        }
      />
    </ConditionWrapper>
  </GridContainerWithNegativeMarginCompensation>
);

LiveDemo.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  retry: PropTypes.func.isRequired,
  showRetry: PropTypes.bool.isRequired
};

export default LiveDemo;

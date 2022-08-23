import React from "react";
import CircularProgress from "@mui/material/CircularProgress";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import ConditionWrapper from "components/ConditionWrapper";
import GridContainerWithNegativeMarginCompensation from "components/GridContainerWithNegativeMarginCompensation";
import Logo from "components/Logo";
import MailTo from "components/MailTo";
import PageTitle from "components/PageTitle";
import { EMAIL_SUPPORT, HOME } from "urls";
import { SPACING_4 } from "utils/layouts";

const ConnectJira = ({ isLoading, isError = false }) => (
  <GridContainerWithNegativeMarginCompensation spacing={SPACING_4} direction="column" alignItems="center">
    <Grid item>
      <Logo width={200} dataTestId="img_logo" />
    </Grid>
    <ConditionWrapper
      condition={isLoading}
      conditionTemplate={
        <>
          <Grid item>
            <PageTitle dataTestId="p_connecting_ju" align="center">
              <FormattedMessage id="connectingJiraUser" />
            </PageTitle>
          </Grid>
          <Grid item>
            <CircularProgress data-test-id="svg_loading" />
          </Grid>
        </>
      }
    >
      <ConditionWrapper
        condition={isError}
        conditionTemplate={
          <>
            <Grid item>
              <PageTitle align="center">
                <FormattedMessage id="somethingWentWrong" />
              </PageTitle>
            </Grid>
            <Grid item>
              <Typography>
                <FormattedMessage
                  id="pleaseContactSupport"
                  values={{
                    supportEmail: (chunks) => <MailTo email={EMAIL_SUPPORT} text={chunks[0]} />
                  }}
                />
              </Typography>
            </Grid>
          </>
        }
      >
        <Grid item>
          <PageTitle align="center">
            <FormattedMessage id="jiraUserConnected" />
          </PageTitle>
        </Grid>
        <Grid item>
          <Typography align="center">
            <FormattedMessage id="jiraUserConnectedOptions" />
          </Typography>
        </Grid>
        <Grid item>
          <Button color="primary" variant="contained" messageId="goToDashboard" size="medium" link={HOME} />
        </Grid>
      </ConditionWrapper>
    </ConditionWrapper>
  </GridContainerWithNegativeMarginCompensation>
);

ConnectJira.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  isError: PropTypes.bool.isRequired
};

export default ConnectJira;

import React from "react";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";
import { Box, Stack } from "@mui/system";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import Logo from "components/Logo";
import MailTo from "components/MailTo";
import PageTitle from "components/PageTitle";
import { EMAIL_SUPPORT, HOME } from "urls";
import { SPACING_4 } from "utils/layouts";

const ConnectJira = ({ isLoading = false, isError = false }) => (
  <Stack spacing={SPACING_4} justifyContent="center" alignItems="center">
    <Box>
      <Logo width={200} dataTestId="img_logo" />
    </Box>
    {isLoading ? (
      <>
        <Box pr={2} pl={2}>
          <PageTitle dataTestId="p_connecting_ju" align="center">
            <FormattedMessage id="connectingJiraUser" />
          </PageTitle>
        </Box>
        <Box height={60}>
          <CircularProgress data-test-id="svg_loading" />
        </Box>
      </>
    ) : (
      <>
        {isError ? (
          <>
            <Box pr={2} pl={2}>
              <PageTitle align="center">
                <FormattedMessage id="somethingWentWrong" />
              </PageTitle>
            </Box>
            <Box pr={2} pl={2}>
              <Typography>
                <FormattedMessage
                  id="pleaseContactSupport"
                  values={{
                    supportEmail: (chunks) => <MailTo email={EMAIL_SUPPORT} text={chunks[0]} />
                  }}
                />
              </Typography>
            </Box>
          </>
        ) : (
          <>
            <Box pr={2} pl={2}>
              <PageTitle align="center">
                <FormattedMessage id="jiraUserConnected" />
              </PageTitle>
            </Box>
            <Box pr={2} pl={2}>
              <Typography align="center">
                <FormattedMessage id="jiraUserConnectedOptions" />
              </Typography>
            </Box>
            <Box>
              <Button color="primary" variant="contained" messageId="goToDashboard" size="medium" link={HOME} />
            </Box>
          </>
        )}
      </>
    )}
  </Stack>
);

ConnectJira.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  isError: PropTypes.bool.isRequired
};

export default ConnectJira;

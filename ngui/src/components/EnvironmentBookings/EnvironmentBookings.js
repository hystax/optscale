import React from "react";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import SubTitle from "components/SubTitle";
import EnvironmentBookingsCalendarContainer from "containers/EnvironmentBookingsCalendarContainer";
import EnvironmentWebhooksContainer from "containers/EnvironmentWebhooksContainer";
import SshRequiredSwitchContainer from "containers/SshRequiredSwitchContainer";
import { SPACING_4 } from "utils/layouts";

const AcquireReleaseHooksTitleInstructions = () => (
  <SubTitle>
    <FormattedMessage id="environmentAcquireReleaseHooks" />
  </SubTitle>
);

const AcquireReleaseHooksDescription = () => (
  <Typography gutterBottom>
    <FormattedMessage
      id="environmentHooksDescription"
      values={{
        br: <br />
      }}
    />
  </Typography>
);

const EnvironmentBookings = ({
  resourceId,
  resourceType,
  isSshRequired,
  cloudResourceId,
  poolId,
  poolName,
  poolType,
  resourceName
}) => (
  <Grid container direction="row" justifyContent="flex-start" spacing={SPACING_4}>
    <Grid item xs={12} lg={6} xl={4}>
      <EnvironmentBookingsCalendarContainer
        resourceId={resourceId}
        resourceType={resourceType}
        resourceName={resourceName}
        cloudResourceId={cloudResourceId}
        poolId={poolId}
        poolName={poolName}
        poolType={poolType}
      />
    </Grid>
    <Grid item xs={12} lg={6} xl={8}>
      <AcquireReleaseHooksTitleInstructions />
      <AcquireReleaseHooksDescription />
      <SshRequiredSwitchContainer environmentId={resourceId} isSshRequired={isSshRequired} />
      <EnvironmentWebhooksContainer resourceId={resourceId} />
    </Grid>
  </Grid>
);

EnvironmentBookings.propTypes = {
  resourceId: PropTypes.string.isRequired,
  resourceType: PropTypes.string.isRequired,
  isSshRequired: PropTypes.bool,
  cloudResourceId: PropTypes.string.isRequired,
  poolId: PropTypes.string.isRequired,
  poolName: PropTypes.string.isRequired,
  poolType: PropTypes.string.isRequired,
  resourceName: PropTypes.string
};

export default EnvironmentBookings;

import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
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

const EnvironmentBookings = ({ resourceId, resourceType, isSshRequired, poolId, poolName, poolType, resourceName }) => (
  <Grid container direction="row" justifyContent="flex-start" spacing={SPACING_4}>
    <Grid item xs={12} lg={6} xl={4}>
      <EnvironmentBookingsCalendarContainer
        resourceId={resourceId}
        resourceType={resourceType}
        resourceName={resourceName}
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

export default EnvironmentBookings;

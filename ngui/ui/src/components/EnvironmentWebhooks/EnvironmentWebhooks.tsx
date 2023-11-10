import Grid from "@mui/material/Grid";
import EnvironmentWebhook from "components/EnvironmentWebhook";
import { BOOKING_ACQUIRE, BOOKING_RELEASE } from "services/WebhooksService";
import { SPACING_2 } from "utils/layouts";

const getTargetWebhooks = (webhooks) =>
  webhooks.reduce(
    (result, webhook) => {
      if (webhook.action === BOOKING_ACQUIRE) {
        return { ...result, acquireWebhook: webhook };
      }
      if (webhook.action === BOOKING_RELEASE) {
        return { ...result, releaseWebhook: webhook };
      }
      return result;
    },
    { acquireWebhook: {}, releaseWebhook: {} }
  );

const EnvironmentWebhooks = ({ webhooks, resourceId, isLoadingProps = {} }) => {
  const { acquireWebhook, releaseWebhook } = getTargetWebhooks(webhooks);

  return (
    <Grid container direction="column" spacing={SPACING_2}>
      <Grid item>
        <EnvironmentWebhook
          webhook={acquireWebhook}
          action={BOOKING_ACQUIRE}
          resourceId={resourceId}
          isLoadingProps={isLoadingProps}
        />
      </Grid>
      <Grid item>
        <EnvironmentWebhook
          webhook={releaseWebhook}
          action={BOOKING_RELEASE}
          resourceId={resourceId}
          isLoadingProps={isLoadingProps}
        />
      </Grid>
    </Grid>
  );
};

export default EnvironmentWebhooks;

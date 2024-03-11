import { useState } from "react";
import CreateOutlinedIcon from "@mui/icons-material/CreateOutlined";
import Box from "@mui/material/Box";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormLabel from "@mui/material/FormLabel";
import { useTheme } from "@mui/material/styles";
import { FormattedMessage } from "react-intl";
import DeleteWebhook from "components/DeleteWebhook";
import IconButton from "components/IconButton";
import InputLoader from "components/InputLoader";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import CreateEnvironmentWebhookFormContainer from "containers/CreateEnvironmentWebhookFormContainer";
import DownloadEnvironmentWebhookAuditLogsContainer from "containers/DownloadEnvironmentWebhookAuditLogsContainer";
import EditEnvironmentWebhookActivityContainer from "containers/EditEnvironmentWebhookActivityContainer";
import EditEnvironmentWebhookFormContainer from "containers/EditEnvironmentWebhookFormContainer";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { ACTIONS } from "services/WebhooksService";
import { isEmpty } from "utils/objects";

const WebhookLabel = ({ labelColor, labelMessageId }) => (
  <FormLabel style={{ color: labelColor }} component="p">
    <FormattedMessage id={labelMessageId} />
  </FormLabel>
);

const EnvironmentWebhook = ({ webhook, action, resourceId, isLoadingProps = {} }) => {
  const theme = useTheme();

  const { id, active, url } = webhook;

  const [isEditMode, setIsEditMode] = useState(false);
  const enableEditMode = () => setIsEditMode(true);
  const disableEditMode = () => setIsEditMode(false);

  const { isDemo } = useOrganizationInfo();

  const canManageBookings = useIsAllowed({ requiredActions: ["MANAGE_RESOURCES"] });

  const { isGetWebhooksLoading = false, isGetResourceAllowedActionsLoading = false } = isLoadingProps;

  const WebhookForm = ({ value, form }) =>
    isEditMode ? (
      form
    ) : (
      <Box display="flex" alignItems="center">
        <KeyValueLabel keyMessageId="url" value={value} sx={{ marginRight: 1 }} />
        {canManageBookings && (
          <IconButton
            disabled={isDemo}
            icon={<CreateOutlinedIcon />}
            onClick={enableEditMode}
            tooltip={{
              show: true,
              messageId: isDemo ? "notAvailableInLiveDemo" : "edit"
            }}
          />
        )}
      </Box>
    );

  const WebhookActions = () => (
    <Box display="flex" alignItems="center">
      {canManageBookings ? (
        <FormControlLabel
          control={<EditEnvironmentWebhookActivityContainer webhookId={id} isActive={active} />}
          label={<FormattedMessage id={ACTIONS[action]} />}
          labelPlacement="start"
          style={{ marginRight: 0, marginLeft: 0 }}
        />
      ) : (
        <WebhookLabel labelMessageId={ACTIONS[action]} />
      )}
      {canManageBookings && <DeleteWebhook id={id} action={ACTIONS[action]} url={url} />}
      <DownloadEnvironmentWebhookAuditLogsContainer webhookId={id} />
    </Box>
  );

  return isGetWebhooksLoading || isGetResourceAllowedActionsLoading ? (
    <InputLoader />
  ) : (
    <>
      {isEmpty(webhook) ? (
        <>
          <WebhookLabel labelColor={theme.palette.text.primary} labelMessageId={ACTIONS[action]} />
          <WebhookForm
            value={<FormattedMessage id="notSet" />}
            form={
              <CreateEnvironmentWebhookFormContainer
                resourceId={resourceId}
                onCancel={disableEditMode}
                onSuccess={disableEditMode}
                action={action}
              />
            }
          />
        </>
      ) : (
        <>
          <WebhookActions />
          <WebhookForm
            value={url}
            form={
              <EditEnvironmentWebhookFormContainer
                webhookId={id}
                onCancel={disableEditMode}
                onSuccess={disableEditMode}
                url={url}
              />
            }
          />
        </>
      )}
    </>
  );
};

export default EnvironmentWebhook;

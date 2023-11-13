import { GET_RESOURCE_ALLOWED_ACTIONS } from "api/auth/actionTypes";
import EnvironmentWebhooks from "components/EnvironmentWebhooks";
import { useApiState } from "hooks/useApiState";
import WebhooksService from "services/WebhooksService";
import { ENVIRONMENT } from "utils/constants";

const EnvironmentWebhooksContainer = ({ resourceId }) => {
  const { useGet } = WebhooksService();

  const requestParams = {
    objectType: ENVIRONMENT,
    objectId: resourceId
  };

  const { isGetWebhooksLoading, webhooks } = useGet(requestParams);

  const { isLoading: isGetResourceAllowedActionsLoading } = useApiState(GET_RESOURCE_ALLOWED_ACTIONS);

  return (
    <EnvironmentWebhooks
      webhooks={webhooks}
      isLoadingProps={{ isGetWebhooksLoading, isGetResourceAllowedActionsLoading }}
      resourceId={resourceId}
    />
  );
};

export default EnvironmentWebhooksContainer;

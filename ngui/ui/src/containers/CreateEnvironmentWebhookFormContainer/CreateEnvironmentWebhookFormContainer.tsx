import EnvironmentWebhookForm from "components/forms/EnvironmentWebhookForm";
import WebhooksService from "services/WebhooksService";
import { ENVIRONMENT } from "utils/constants";

const CreateEnvironmentWebhookFormContainer = ({ resourceId, onSuccess, onCancel, action }) => {
  const { useCreate } = WebhooksService();

  const { create, isCreateWebhookLoading } = useCreate();

  const onSubmit = (newUrl) => {
    create({ objectId: resourceId, objectType: ENVIRONMENT, url: newUrl, action, onSuccess });
  };

  return <EnvironmentWebhookForm onSubmit={onSubmit} onCancel={onCancel} isLoading={isCreateWebhookLoading} />;
};

export default CreateEnvironmentWebhookFormContainer;

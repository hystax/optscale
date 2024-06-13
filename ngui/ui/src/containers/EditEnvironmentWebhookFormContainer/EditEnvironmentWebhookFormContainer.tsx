import EnvironmentWebhookForm from "components/forms/EnvironmentWebhookForm";
import WebhooksService from "services/WebhooksService";

const EditEnvironmentWebhookFormContainer = ({ webhookId, onSuccess, onCancel, url }) => {
  const { useUpdate } = WebhooksService();

  const { update, isUpdateWebhookLoading } = useUpdate();

  const onSubmit = (newUrl) => {
    update({ webhookId, url: newUrl, onSuccess });
  };

  return <EnvironmentWebhookForm url={url} onSubmit={onSubmit} onCancel={onCancel} isLoading={isUpdateWebhookLoading} />;
};

export default EditEnvironmentWebhookFormContainer;

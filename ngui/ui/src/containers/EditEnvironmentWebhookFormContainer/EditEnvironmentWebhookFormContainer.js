import React from "react";
import PropTypes from "prop-types";
import EnvironmentWebhookForm from "components/EnvironmentWebhookForm";
import WebhooksService from "services/WebhooksService";

const EditEnvironmentWebhookFormContainer = ({ webhookId, onSuccess, onCancel, url }) => {
  const { useUpdate } = WebhooksService();

  const { update, isUpdateWebhookLoading } = useUpdate();

  const onSubmit = (newUrl) => {
    update({ webhookId, url: newUrl, onSuccess });
  };

  return <EnvironmentWebhookForm url={url} onSubmit={onSubmit} onCancel={onCancel} isLoading={isUpdateWebhookLoading} />;
};

EditEnvironmentWebhookFormContainer.propTypes = {
  webhookId: PropTypes.string.isRequired,
  onSuccess: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  url: PropTypes.string
};

export default EditEnvironmentWebhookFormContainer;

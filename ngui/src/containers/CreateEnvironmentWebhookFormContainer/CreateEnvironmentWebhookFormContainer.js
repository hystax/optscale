import React from "react";
import PropTypes from "prop-types";
import EnvironmentWebhookForm from "components/EnvironmentWebhookForm";
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

CreateEnvironmentWebhookFormContainer.propTypes = {
  resourceId: PropTypes.string.isRequired,
  onSuccess: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  action: PropTypes.string.isRequired,
  url: PropTypes.string
};

export default CreateEnvironmentWebhookFormContainer;

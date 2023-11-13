import { useIntl } from "react-intl";
import DeleteEntity from "components/DeleteEntity";
import WebhooksService from "services/WebhooksService";

const DeleteWebhookContainer = ({ id, action, url, onCancel }) => {
  const intl = useIntl();

  const { useDelete } = WebhooksService();
  const { deleteWebhook, isRemoveWebhookLoading: isLoading } = useDelete();

  const onSubmit = () => {
    deleteWebhook({ webhookId: id, onSuccess: onCancel });
  };

  return (
    <DeleteEntity
      onDelete={onSubmit}
      onCancel={onCancel}
      isLoading={isLoading}
      deleteButtonProps={{
        onDelete: onSubmit
      }}
      dataTestIds={{
        text: "p_delete",
        deleteButton: "btn_smodal_delete",
        cancelButton: "btn_cancel"
      }}
      message={{
        messageId: "deleteWebhookQuestion",
        values: {
          action: intl.formatMessage({ id: action }).toLowerCase(),
          url
        }
      }}
    />
  );
};

export default DeleteWebhookContainer;

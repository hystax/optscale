import DeleteWebhookContainer from "containers/DeleteWebhookContainer";
import BaseSideModal from "./BaseSideModal";

class DeleteWebhookModal extends BaseSideModal {
  headerProps = {
    messageId: "deleteWebhookTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_webhook",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete_webhook";

  get content() {
    return (
      <DeleteWebhookContainer
        id={this.payload?.id}
        action={this.payload?.action}
        url={this.payload?.url}
        onCancel={this.closeSideModal}
      />
    );
  }
}

export default DeleteWebhookModal;

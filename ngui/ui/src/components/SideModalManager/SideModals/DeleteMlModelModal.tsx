import DeleteMlModelContainer from "containers/DeleteMlModelContainer";
import BaseSideModal from "./BaseSideModal";

class DeleteMlModelModal extends BaseSideModal {
  headerProps = {
    messageId: "deleteModelTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_model",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete";

  get content() {
    return (
      <DeleteMlModelContainer
        onCancel={this.closeSideModal}
        onSuccess={this.payload?.onSuccess}
        modelId={this.payload?.modelId}
        modelName={this.payload?.modelName}
      />
    );
  }
}

export default DeleteMlModelModal;

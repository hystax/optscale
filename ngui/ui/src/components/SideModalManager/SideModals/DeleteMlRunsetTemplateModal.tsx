import DeleteMlRunsetTemplateContainer from "containers/DeleteMlRunsetTemplateContainer";
import BaseSideModal from "./BaseSideModal";

class DeleteMlRunsetTemplateModal extends BaseSideModal {
  headerProps = {
    messageId: "deleteMlRunsetTemplateTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_pool",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete";

  get content() {
    return <DeleteMlRunsetTemplateContainer id={this.payload?.runsetTemplateId} onCancel={this.closeSideModal} />;
  }
}

export default DeleteMlRunsetTemplateModal;

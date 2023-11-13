import DeleteMlGlobalParameterContainer from "containers/DeleteMlGlobalParameterContainer/DeleteMlGlobalParameterContainer";
import BaseSideModal from "./BaseSideModal";

class DeleteMlGlobalParameterModal extends BaseSideModal {
  headerProps = {
    messageId: "deleteGlobalParameterTitle",
    color: "error",
    dataTestIds: {
      title: "title_delete_global_parameter",
      closeButton: "close_btn"
    }
  };

  dataTestId = "smodal_delete_global_parameter";

  get content() {
    return <DeleteMlGlobalParameterContainer id={this.payload?.id} name={this.payload?.name} onCancel={this.closeSideModal} />;
  }
}

export default DeleteMlGlobalParameterModal;

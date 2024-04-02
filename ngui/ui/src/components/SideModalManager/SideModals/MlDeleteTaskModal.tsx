import MlDeleteTaskContainer from "containers/MlDeleteTaskContainer";
import BaseSideModal from "./BaseSideModal";

class MlDeleteTaskModal extends BaseSideModal {
  headerProps = {
    messageId: "mlDeleteTaskTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_ml_task",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete";

  get content() {
    return <MlDeleteTaskContainer id={this.payload?.id} name={this.payload?.name} onCancel={this.closeSideModal} />;
  }
}

export default MlDeleteTaskModal;

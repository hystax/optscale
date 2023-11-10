import MlDeleteModelContainer from "containers/MlDeleteModelContainer";
import BaseSideModal from "./BaseSideModal";

class MlDeleteModelModal extends BaseSideModal {
  headerProps = {
    messageId: "mlDeleteModelTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_ml_model",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete";

  get content() {
    return <MlDeleteModelContainer id={this.payload?.id} name={this.payload?.name} onCancel={this.closeSideModal} />;
  }
}

export default MlDeleteModelModal;

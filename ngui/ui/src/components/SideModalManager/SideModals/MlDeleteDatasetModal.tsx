import MlDeleteDatasetContainer from "containers/MlDeleteDatasetContainer";
import BaseSideModal from "./BaseSideModal";

class MlDeleteDatasetModal extends BaseSideModal {
  headerProps = {
    messageId: "mlDeleteDatasetTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_ml_dataset",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete";

  get content() {
    return <MlDeleteDatasetContainer id={this.payload?.id} path={this.payload?.path} closeSideModal={this.closeSideModal} />;
  }
}

export default MlDeleteDatasetModal;

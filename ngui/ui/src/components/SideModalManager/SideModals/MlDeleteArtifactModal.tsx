import MlDeleteArtifactContainer from "containers/MlDeleteArtifactContainer";
import BaseSideModal from "./BaseSideModal";

class MlDeleteArtifactModal extends BaseSideModal {
  headerProps = {
    messageId: "mlDeleteArtifactTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_ml_artifact",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete";

  get content() {
    return (
      <MlDeleteArtifactContainer
        id={this.payload?.id}
        name={this.payload?.name}
        onSuccess={this.payload?.onSuccess}
        closeSideModal={this.closeSideModal}
      />
    );
  }
}

export default MlDeleteArtifactModal;

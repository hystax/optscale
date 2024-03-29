import EditModelVersionPathFormContainer from "containers/EditModelVersionPathFormContainer";
import BaseSideModal from "./BaseSideModal";

class EditModelPathModal extends BaseSideModal {
  headerProps = {
    messageId: "manageVersionPathTitle",
    dataTestIds: {
      title: "lbl_edit_version_path",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_edit_version_path";

  get content() {
    return (
      <EditModelVersionPathFormContainer
        modelId={this.payload?.modelId}
        modelVersion={this.payload?.modelVersion}
        onCancel={this.closeSideModal}
        onSuccess={this.closeSideModal}
      />
    );
  }
}

export default EditModelPathModal;

import EditModelVersionTagsFormContainer from "containers/EditModelVersionTagsFormContainer";
import BaseSideModal from "./BaseSideModal";

class EditModelVersionTagsModal extends BaseSideModal {
  headerProps = {
    messageId: "manageVersionTagsTitle",
    dataTestIds: {
      title: "lbl_edit_version_tags",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_edit_version_tags";

  get content() {
    return (
      <EditModelVersionTagsFormContainer
        modelId={this.payload?.modelId}
        modelVersion={this.payload?.modelVersion}
        onCancel={this.closeSideModal}
        onSuccess={this.closeSideModal}
      />
    );
  }
}

export default EditModelVersionTagsModal;

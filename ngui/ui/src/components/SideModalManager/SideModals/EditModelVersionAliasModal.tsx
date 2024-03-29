import EditModelVersionAliasFormContainer from "containers/EditModelVersionAliasFormContainer";
import BaseSideModal from "./BaseSideModal";

class EditModelVersionModal extends BaseSideModal {
  headerProps = {
    messageId: "manageVersionAliasesTitle",
    dataTestIds: {
      title: "lbl_edit_version_aliases",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_edit_version_aliases";

  get content() {
    return (
      <EditModelVersionAliasFormContainer
        modelId={this.payload?.modelId}
        modelVersion={this.payload?.modelVersion}
        aliasToVersionMap={this.payload?.aliasToVersionMap}
        onCancel={this.closeSideModal}
        onSuccess={this.closeSideModal}
      />
    );
  }
}

export default EditModelVersionModal;

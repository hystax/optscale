import DeleteGlobalResourceConstraintContainer from "containers/DeleteGlobalResourceConstraintContainer";
import BaseSideModal from "./BaseSideModal";

class DeleteGlobalResourceConstraintModal extends BaseSideModal {
  headerProps = {
    messageId: "deleteResourceConstraintTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_resource_constraint",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete";

  get content() {
    return (
      <DeleteGlobalResourceConstraintContainer
        constraintId={this.payload?.id}
        constraintType={this.payload?.type}
        resourceName={this.payload?.resourceName}
        cloudResourceId={this.payload?.cloudResourceId}
        closeSideModal={this.closeSideModal}
      />
    );
  }
}

export default DeleteGlobalResourceConstraintModal;

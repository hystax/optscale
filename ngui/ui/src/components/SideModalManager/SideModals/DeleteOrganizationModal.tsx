import DeleteOrganizationContainer from "containers/DeleteOrganizationContainer";
import BaseSideModal from "./BaseSideModal";

class DeleteOrganizationModal extends BaseSideModal {
  headerProps = {
    messageId: "deleteOrganizationTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_organization",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete_organization";

  get content() {
    return <DeleteOrganizationContainer onCancel={this.closeSideModal} />;
  }
}

export default DeleteOrganizationModal;

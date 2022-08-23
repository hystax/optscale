import React from "react";
import DeleteOrganizationOptionContainer from "containers/DeleteOrganizationOptionContainer";
import BaseSideModal from "./BaseSideModal";

class DeleteOrganizationOptionModal extends BaseSideModal {
  headerProps = {
    messageId: "deleteOrganizationOptionTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_organization_option",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete_organization_option";

  get content() {
    return <DeleteOrganizationOptionContainer name={this.payload?.name} onCancel={this.closeSideModal} />;
  }
}

export default DeleteOrganizationOptionModal;

import React from "react";
import CreateOrganizationContainer from "containers/CreateOrganizationContainer";
import BaseSideModal from "./BaseSideModal";

class CreateOrganizationModal extends BaseSideModal {
  headerProps = {
    messageId: "createNewOrganizationTitle",
    dataTestIds: {
      title: "lbl_create_new_organization",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_create_new_organization";

  get content() {
    return <CreateOrganizationContainer closeSideModal={this.closeSideModal} onSuccess={this.payload?.onSuccess} />;
  }
}

export default CreateOrganizationModal;

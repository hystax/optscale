import React from "react";
import CreateOrganizationOptionContainer from "containers/CreateOrganizationOptionContainer";
import BaseSideModal from "./BaseSideModal";

class CreateOrganizationOptionModal extends BaseSideModal {
  headerProps = {
    messageId: "createOrganizationOptionTitle",
    dataTestIds: {
      title: "lbl_create",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_create";

  get content() {
    return <CreateOrganizationOptionContainer onCancel={this.closeSideModal} />;
  }
}

export default CreateOrganizationOptionModal;

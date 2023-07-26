import React from "react";
import DeleteEnvironmentContainer from "containers/DeleteEnvironmentContainer";
import BaseSideModal from "./BaseSideModal";

class DeleteEnvironmentModal extends BaseSideModal {
  headerProps = {
    messageId: "deleteItEnvironmentTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_environment",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete";

  get content() {
    return <DeleteEnvironmentContainer id={this.payload?.id} name={this.payload?.name} onCancel={this.closeSideModal} />;
  }
}

export default DeleteEnvironmentModal;

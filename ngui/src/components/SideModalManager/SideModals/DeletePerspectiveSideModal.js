import React from "react";
import DeleteResourcePerspectiveContainer from "containers/DeleteResourcePerspectiveContainer";
import BaseSideModal from "./BaseSideModal";

class DeletePerspectiveSideModal extends BaseSideModal {
  headerProps = {
    messageId: "deletePerspectiveTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete_perspective";

  get content() {
    return (
      <DeleteResourcePerspectiveContainer
        perspectiveName={this.payload?.perspectiveName}
        onSuccess={this.closeSideModal}
        onCancel={this.closeSideModal}
      />
    );
  }
}

export default DeletePerspectiveSideModal;

import React from "react";
import DeletePoolContainer from "containers/DeletePoolContainer";
import BaseSideModal from "./BaseSideModal";

class DeletePoolModal extends BaseSideModal {
  headerProps = {
    messageId: "deletePoolTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_pool",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete";

  contentPadding = 0;

  get content() {
    return <DeletePoolContainer id={this.payload?.poolId} onCancel={this.closeSideModal} />;
  }
}

export default DeletePoolModal;

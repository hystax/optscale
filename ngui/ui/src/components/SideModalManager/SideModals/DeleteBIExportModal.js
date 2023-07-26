import React from "react";
import DeleteBIExportContainer from "containers/DeleteBIExportContainer";
import BaseSideModal from "./BaseSideModal";

class DeleteBIExportModal extends BaseSideModal {
  headerProps = {
    messageId: "deleteBIExportTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_bi_export",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete";

  get content() {
    return <DeleteBIExportContainer id={this.payload?.biExportId} onCancel={this.closeSideModal} />;
  }
}

export default DeleteBIExportModal;

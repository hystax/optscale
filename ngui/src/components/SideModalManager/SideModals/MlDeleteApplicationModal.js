import React from "react";
import MlDeleteApplicationContainer from "containers/MlDeleteApplicationContainer";
import BaseSideModal from "./BaseSideModal";

class MlDeleteApplicationModal extends BaseSideModal {
  headerProps = {
    messageId: "mlDeleteApplicationTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_ml_application",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete";

  get content() {
    return <MlDeleteApplicationContainer id={this.payload?.id} name={this.payload?.name} onCancel={this.closeSideModal} />;
  }
}

export default MlDeleteApplicationModal;

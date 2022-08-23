import React from "react";
import DisconnectCloudAccountContainer from "containers/DisconnectCloudAccountContainer";
import BaseSideModal from "./BaseSideModal";

class DisconnectCloudAccountModal extends BaseSideModal {
  get headerProps() {
    return {
      messageId: "disconnect:entity",
      color: "error",
      formattedMessageValues: { name: this.payload?.name },
      dataTestIds: {
        title: "lbl_disconnect",
        closeButton: "btn_close"
      }
    };
  }

  dataTestId = "smodal_disconnect";

  get content() {
    return <DisconnectCloudAccountContainer id={this.payload?.id} type={this.payload?.type} onCancel={this.closeSideModal} />;
  }
}

export default DisconnectCloudAccountModal;

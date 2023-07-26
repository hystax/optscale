import React from "react";
import DisconnectGoogleCalendarContainer from "containers/DisconnectGoogleCalendarContainer";
import BaseSideModal from "./BaseSideModal";

class DisconnectGoogleCalendarModal extends BaseSideModal {
  headerProps = {
    messageId: "disconnectGoogleCalendarTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_disconnect",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_disconnect_google_calendar";

  get content() {
    return (
      <DisconnectGoogleCalendarContainer
        id={this.payload?.id}
        shareableLink={this.payload?.shareable_link}
        onCancel={this.closeSideModal}
      />
    );
  }
}

export default DisconnectGoogleCalendarModal;

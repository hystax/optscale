import React from "react";
import DeleteBookingContainer from "containers/DeleteBookingContainer";
import BaseSideModal from "./BaseSideModal";

class DeleteEnvironmentBookingModal extends BaseSideModal {
  headerProps = {
    messageId: "deleteBookingTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_booking",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete_booking";

  get content() {
    return (
      <DeleteBookingContainer
        bookingId={this.payload?.bookingId}
        onSuccess={this.closeSideModal}
        onCancel={this.closeSideModal}
      />
    );
  }
}

export default DeleteEnvironmentBookingModal;

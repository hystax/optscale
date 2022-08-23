import React from "react";
import AcceptAssignmentRequestForm from "components/AcceptAssignmentRequestForm";
import BaseSideModal from "./BaseSideModal";

class AcceptAssignmentRequestModal extends BaseSideModal {
  headerProps = {
    messageId: "acceptAssignmentRequestTitle",
    dataTestIds: {
      title: "lbl_accept_assignment",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_accept";

  get content() {
    return (
      <AcceptAssignmentRequestForm
        assignmentRequestId={this.payload?.assignmentRequestId}
        resourceName={this.payload?.resourceName}
        closeSideModal={this.closeSideModal}
      />
    );
  }
}

export default AcceptAssignmentRequestModal;

import React from "react";
import ApplyResourcePerspective from "components/ApplyResourcePerspective";
import BaseSideModal from "./BaseSideModal";

class ApplyResourcePerspectiveModal extends BaseSideModal {
  headerProps = {
    messageId: "perspectivesTitle",
    dataTestIds: {
      title: "lbl_perspectives",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_perspective";

  get content() {
    return (
      <ApplyResourcePerspective
        perspectives={this.payload?.perspectives}
        appliedPerspectiveName={this.payload?.appliedPerspectiveName}
        onApply={this.payload?.onApply}
        onCancel={this.closeSideModal}
      />
    );
  }
}

export default ApplyResourcePerspectiveModal;

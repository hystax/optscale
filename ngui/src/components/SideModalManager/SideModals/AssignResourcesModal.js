import React from "react";
import SplitResourcesContainer from "containers/SplitResourcesContainer";
import BaseSideModal from "./BaseSideModal";

class AssignResourcesModal extends BaseSideModal {
  headerProps = {
    messageId: "assignResourcesTitle",
    dataTestIds: {
      title: "lbl_assign",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_assign";

  // using accordions inside modal — looks better without padding
  contentPadding = 0;

  get content() {
    return <SplitResourcesContainer resourcesIds={this.payload?.resourceIds} closeSideModal={this.closeSideModal} />;
  }
}

export default AssignResourcesModal;

import React from "react";
import StagesAndMilestonesContainer from "containers/StagesAndMilestonesContainer";
import BaseSideModal from "./BaseSideModal";

class SelectStageOrMilestoneModal extends BaseSideModal {
  headerProps = {
    messageId: "selectStageOrMilestone",
    dataTestIds: {
      title: "lbl_select_stage_or_milestone",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_select_stage_or_milestone";

  get content() {
    return <StagesAndMilestonesContainer {...this.payload} closeSideModal={this.closeSideModal} />;
  }
}

export default SelectStageOrMilestoneModal;

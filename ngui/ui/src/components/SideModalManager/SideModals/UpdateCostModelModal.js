import React from "react";
import CostModelFormContainer from "containers/CostModelFormContainer";
import BaseSideModal from "./BaseSideModal";

class UpdateCostModelModal extends BaseSideModal {
  headerProps = {
    messageId: "updateCostModelTitle",
    color: "primary",
    dataTestIds: {
      title: "lbl_update_cost_model",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_update_cost_model";

  get content() {
    return (
      <CostModelFormContainer
        cloudAccountId={this.payload?.cloudAccountId}
        costModel={this.payload?.costModel}
        onSuccess={this.closeSideModal}
        onCancel={this.closeSideModal}
      />
    );
  }
}

export default UpdateCostModelModal;

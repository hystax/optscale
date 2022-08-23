import React from "react";
import UpdateCostModelWarning from "components/UpdateCostModelWarning/UpdateCostModelWarning";
import EnvironmentCostModelFormContainer from "containers/EnvironmentCostModelFormContainer";
import { COST_MODEL_TYPES } from "utils/constants";
import BaseSideModal from "./BaseSideModal";

class EnvironmentCostModelModal extends BaseSideModal {
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
      <>
        <UpdateCostModelWarning costModelType={COST_MODEL_TYPES.ENVIRONMENT} />
        <EnvironmentCostModelFormContainer
          resourceId={this.payload?.resourceId}
          hourlyPrice={this.payload?.hourlyPrice}
          onCancel={this.closeSideModal}
        />
      </>
    );
  }
}

export default EnvironmentCostModelModal;

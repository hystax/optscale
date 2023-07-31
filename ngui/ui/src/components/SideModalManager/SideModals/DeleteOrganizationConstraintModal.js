import React from "react";
import DeleteOrganizationConstraintContainer from "containers/DeleteOrganizationConstraintContainer";
import { ANOMALY_TYPES, QUOTAS_AND_BUDGETS_TYPES, TAGGING_POLICY_TYPES } from "utils/constants";
import BaseSideModal from "./BaseSideModal";

class DeleteOrganizationConstraintModal extends BaseSideModal {
  get headerProps() {
    let messageId = "";
    if (ANOMALY_TYPES[this.payload?.type]) {
      messageId = "deleteAnomalyDetectionPolicyTitle";
    }
    if (QUOTAS_AND_BUDGETS_TYPES[this.payload?.type]) {
      messageId = "deleteQuotaAndBudgetPolicyTitle";
    }
    if (TAGGING_POLICY_TYPES[this.payload?.type]) {
      messageId = "deleteTaggingPolicyTitle";
    }

    return {
      messageId,
      color: "error",
      dataTestIds: {
        title: "lbl_delete",
        closeButton: "btn_close"
      }
    };
  }

  dataTestId = "smodal_delete";

  get content() {
    return (
      <DeleteOrganizationConstraintContainer
        id={this.payload?.id}
        name={this.payload?.name}
        onCancel={this.closeSideModal}
        type={this.payload?.type}
      />
    );
  }
}

export default DeleteOrganizationConstraintModal;

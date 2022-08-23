import React from "react";
import DeleteAssignmentRuleContainer from "containers/DeleteAssignmentRuleContainer";
import BaseSideModal from "./BaseSideModal";

class DeleteAssignmentRuleModal extends BaseSideModal {
  headerProps = {
    messageId: "deleteAssignmentRuleTitle",
    color: "error",
    dataTestIds: {
      title: "title_delete_rule",
      closeButton: "close_btn"
    }
  };

  dataTestId = "smodal_delete_assignment_rule";

  get content() {
    return <DeleteAssignmentRuleContainer ruleId={this.payload?.ruleId} closeSideModal={this.closeSideModal} />;
  }
}

export default DeleteAssignmentRuleModal;

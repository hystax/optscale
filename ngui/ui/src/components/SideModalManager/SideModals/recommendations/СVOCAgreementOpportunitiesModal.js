import React from "react";
import BaseSideModal from "../BaseSideModal";
import DaysThreshold from "./components/DaysThreshold";

class СVOCAgreementOpportunitiesModal extends BaseSideModal {
  headerProps = {
    messageId: "cvosAgreementOpportunities",
    dataTestIds: {
      title: "lbl_cvoc_agreement_opportunities_sidemodal_title",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_cvoc_agreement_opportunities";

  get content() {
    return (
      <DaysThreshold
        messageId={"thresholds.cvosAgreementOpportunities"}
        recommendationType={this.payload?.recommendationType}
        onSuccess={this.closeSideModal}
      />
    );
  }
}

export default СVOCAgreementOpportunitiesModal;

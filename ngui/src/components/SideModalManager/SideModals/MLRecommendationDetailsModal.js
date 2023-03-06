import React from "react";
import RecommendationDescription from "components/RecommendationDescription";
import Table from "components/Table";
import BaseSideModal from "./BaseSideModal";

class MLRecommendationDetailsModal extends BaseSideModal {
  get headerProps() {
    return {
      messageId: this.payload.titleMessageId,
      dataTestIds: {
        title: "lbl_ml_sidemodal_title",
        closeButton: "btn_close"
      }
    };
  }

  dataTestId = "smodal_ml_rec_details";

  get content() {
    return (
      <>
        <RecommendationDescription messageId={this.payload?.descriptionMessageId} isLoading={this.payload?.isLoading} />
        <Table columns={this.payload?.columns} data={this.payload?.items} />
      </>
    );
  }
}

export default MLRecommendationDetailsModal;

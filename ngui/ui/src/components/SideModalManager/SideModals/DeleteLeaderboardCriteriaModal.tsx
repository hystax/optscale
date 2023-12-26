import React from "react";
import DeleteLeaderboardDatasetContainer from "containers/DeleteLeaderboardDatasetContainer";
import BaseSideModal from "./BaseSideModal";

class DeleteLeaderboardCriteriaModal extends BaseSideModal {
  headerProps = {
    messageId: "deleteLeaderboardCriteria",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_leaderboard_dataset",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete_leaderboard_dataset";

  get content() {
    return (
      <DeleteLeaderboardDatasetContainer
        onCancel={this.closeSideModal}
        onSuccess={this.closeSideModal}
        leaderboardDataset={this.payload?.leaderboardDataset}
      />
    );
  }
}

export default DeleteLeaderboardCriteriaModal;

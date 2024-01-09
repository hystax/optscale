import CloneLeaderboardDatasetFormContainer from "containers/CloneLeaderboardDatasetFormContainer";
import BaseSideModal from "./BaseSideModal";

class CloneLeaderboardDatasetModal extends BaseSideModal {
  headerProps = {
    messageId: "cloneLeaderboardCriteria",
    showExpand: true,
    dataTestIds: {
      title: "lbl_clone_leaderboard_dataset",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_clone_leaderboard_dataset";

  get content() {
    return (
      <CloneLeaderboardDatasetFormContainer
        onCancel={this.closeSideModal}
        onSuccess={this.closeSideModal}
        leaderboard={this.payload?.leaderboard}
        leaderboardDataset={this.payload?.leaderboardDataset}
      />
    );
  }
}

export default CloneLeaderboardDatasetModal;

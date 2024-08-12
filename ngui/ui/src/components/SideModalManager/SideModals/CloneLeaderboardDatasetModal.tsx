import CloneLeaderboardDatasetFormContainer from "containers/CloneLeaderboardDatasetFormContainer";
import BaseSideModal from "./BaseSideModal";

class CloneLeaderboardDatasetModal extends BaseSideModal {
  headerProps = {
    messageId: "cloneLeaderboardTitle",
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
        onSuccess={(newLeaderboardDataset) => {
          this.payload?.onSuccess?.(newLeaderboardDataset);
          this.closeSideModal();
        }}
        task={this.payload?.task}
        leaderboard={this.payload?.leaderboard}
        leaderboardDataset={this.payload?.leaderboardDataset}
      />
    );
  }
}

export default CloneLeaderboardDatasetModal;

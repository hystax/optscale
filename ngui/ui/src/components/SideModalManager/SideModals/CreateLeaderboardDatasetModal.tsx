import CreateLeaderboardDatasetFormContainer from "containers/CreateLeaderboardDatasetFormContainer";
import BaseSideModal from "./BaseSideModal";

class CreateLeaderboardDatasetModal extends BaseSideModal {
  headerProps = {
    messageId: "defineLeaderboardTitle",
    showExpand: true,
    dataTestIds: {
      title: "lbl_create_leaderboard_dataset",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_create_leaderboard_dataset";

  get content() {
    return (
      <CreateLeaderboardDatasetFormContainer
        task={this.payload?.task}
        leaderboard={this.payload?.leaderboard}
        onCancel={this.closeSideModal}
        onSuccess={(newLeaderboardDataset) => {
          this.payload?.onSuccess?.(newLeaderboardDataset);
          this.closeSideModal();
        }}
      />
    );
  }
}

export default CreateLeaderboardDatasetModal;

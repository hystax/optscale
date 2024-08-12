import EditLeaderboardDatasetFormContainer from "containers/EditLeaderboardDatasetFormContainer";
import BaseSideModal from "./BaseSideModal";

class EditLeaderboardDatasetModal extends BaseSideModal {
  headerProps = {
    messageId: "editLeaderboardTitle",
    showExpand: true,
    dataTestIds: {
      title: "lbl_edit_leaderboard_dataset",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_edit_leaderboard_dataset";

  get content() {
    return (
      <EditLeaderboardDatasetFormContainer
        onCancel={this.closeSideModal}
        onSuccess={(newLeaderboardDataset) => {
          this.payload?.onSuccess?.(newLeaderboardDataset);
          this.closeSideModal();
        }}
        task={this.payload?.task}
        leaderboardDataset={this.payload?.leaderboardDataset}
      />
    );
  }
}

export default EditLeaderboardDatasetModal;

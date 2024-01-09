import EditLeaderboardDatasetFormContainer from "containers/EditLeaderboardDatasetFormContainer";
import BaseSideModal from "./BaseSideModal";

class EditLeaderboardDatasetModal extends BaseSideModal {
  headerProps = {
    messageId: "editLeaderboardCriteria",
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
        onSuccess={this.closeSideModal}
        leaderboardDataset={this.payload?.leaderboardDataset}
      />
    );
  }
}

export default EditLeaderboardDatasetModal;

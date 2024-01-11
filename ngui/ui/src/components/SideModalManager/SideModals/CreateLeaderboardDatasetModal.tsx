import CreateLeaderboardDatasetFormContainer from "containers/CreateLeaderboardDatasetFormContainer";
import BaseSideModal from "./BaseSideModal";

class CreateLeaderboardDatasetModal extends BaseSideModal {
  headerProps = {
    messageId: "defineLeaderboardCriteria",
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
        leaderboardId={this.payload?.leaderboardId}
        onCancel={this.closeSideModal}
        onSuccess={this.closeSideModal}
      />
    );
  }
}

export default CreateLeaderboardDatasetModal;

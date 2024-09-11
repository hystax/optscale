import DeleteLeaderboardContainer from "containers/DeleteLeaderboardContainer";
import BaseSideModal from "./BaseSideModal";

class DeleteLeaderboardModal extends BaseSideModal {
  headerProps = {
    messageId: "deleteLeaderboardTitle",
    color: "error",
    dataTestIds: {
      title: "lbl_delete_leaderboard",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_delete_leaderboard";

  get content() {
    return (
      <DeleteLeaderboardContainer
        onCancel={this.closeSideModal}
        onSuccess={() => {
          this.payload?.onSuccess?.();
          this.closeSideModal();
        }}
        leaderboard={this.payload?.leaderboard}
      />
    );
  }
}

export default DeleteLeaderboardModal;

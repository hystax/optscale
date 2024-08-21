import CloneLeaderboardFormContainer from "containers/CloneLeaderboardFormContainer";
import BaseSideModal from "./BaseSideModal";

class CloneLeaderboardModal extends BaseSideModal {
  headerProps = {
    messageId: "cloneLeaderboardTitle",
    showExpand: true,
    dataTestIds: {
      title: "lbl_clone_leaderboard",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_clone_leaderboard";

  get content() {
    return (
      <CloneLeaderboardFormContainer
        onCancel={this.closeSideModal}
        onSuccess={(newLeaderboard) => {
          this.payload?.onSuccess?.(newLeaderboard);
          this.closeSideModal();
        }}
        task={this.payload?.task}
        leaderboardTemplate={this.payload?.leaderboardTemplate}
        leaderboard={this.payload?.leaderboard}
      />
    );
  }
}

export default CloneLeaderboardModal;

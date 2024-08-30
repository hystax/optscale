import CreateLeaderboardFormContainer from "containers/CreateLeaderboardFormContainer";
import BaseSideModal from "./BaseSideModal";

class CreateLeaderboardModal extends BaseSideModal {
  headerProps = {
    messageId: "defineLeaderboardTitle",
    showExpand: true,
    dataTestIds: {
      title: "lbl_create_leaderboard",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_create_leaderboard";

  get content() {
    return (
      <CreateLeaderboardFormContainer
        task={this.payload?.task}
        leaderboardTemplate={this.payload?.leaderboardTemplate}
        onCancel={this.closeSideModal}
        onSuccess={(newLeaderboard) => {
          this.payload?.onSuccess?.(newLeaderboard);
          this.closeSideModal();
        }}
      />
    );
  }
}

export default CreateLeaderboardModal;

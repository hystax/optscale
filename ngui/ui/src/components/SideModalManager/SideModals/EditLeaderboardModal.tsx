import EditLeaderboardFormContainer from "containers/EditLeaderboardFormContainer";
import BaseSideModal from "./BaseSideModal";

class EditLeaderboardModal extends BaseSideModal {
  headerProps = {
    messageId: "editLeaderboardTitle",
    showExpand: true,
    dataTestIds: {
      title: "lbl_edit_leaderboard",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_edit_leaderboard";

  get content() {
    return (
      <EditLeaderboardFormContainer
        onCancel={this.closeSideModal}
        onSuccess={(updatedLeaderboard) => {
          this.payload?.onSuccess?.(updatedLeaderboard);
          this.closeSideModal();
        }}
        task={this.payload?.task}
        leaderboard={this.payload?.leaderboard}
      />
    );
  }
}

export default EditLeaderboardModal;

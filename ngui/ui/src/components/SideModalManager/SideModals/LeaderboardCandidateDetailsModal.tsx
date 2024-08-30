import { FormattedMessage } from "react-intl";
import LeaderboardCandidateDetailsModalContent from "components/LeaderboardCandidateDetailsModalContent";
import BaseSideModal from "./BaseSideModal";

class LeaderboardCandidateDetailsModal extends BaseSideModal {
  get headerProps() {
    return {
      text: this.payload?.groupDetails?.note ?? <FormattedMessage id="candidateDetails" />,
      color: "primary",
      showExpand: true,
      dataTestIds: {
        title: "lbl_candidate_details_title",
        closeButton: "btn_close"
      }
    };
  }

  dataTestId = "smodal_candidate_details";

  get content() {
    return (
      <LeaderboardCandidateDetailsModalContent
        taskId={this.payload?.taskId}
        candidateDetails={this.payload?.candidateDetails}
        leaderboard={this.payload?.leaderboard}
        onClose={this.closeSideModal}
      />
    );
  }
}

export default LeaderboardCandidateDetailsModal;

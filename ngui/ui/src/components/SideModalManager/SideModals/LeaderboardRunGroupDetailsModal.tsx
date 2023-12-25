import React from "react";
import { FormattedMessage } from "react-intl";
import LeaderboardRunGroupDetailsModalContent from "components/LeaderboardRunGroupDetailsModalContent";
import BaseSideModal from "./BaseSideModal";

class LeaderboardRunGroupDetailsModal extends BaseSideModal {
  get headerProps() {
    return {
      text: this.payload?.groupDetails?.note ?? <FormattedMessage id="details" />,
      color: "primary",
      showExpand: true,
      dataTestIds: {
        title: "lbl_run_group_details_title",
        closeButton: "btn_close"
      }
    };
  }

  dataTestId = "smodal_run_group_details";

  get content() {
    return (
      <LeaderboardRunGroupDetailsModalContent
        taskId={this.payload?.taskId}
        groupDetails={this.payload?.groupDetails}
        leaderboardDataset={this.payload?.leaderboardDataset}
        onClose={this.closeSideModal}
      />
    );
  }
}

export default LeaderboardRunGroupDetailsModal;

import React from "react";
import BaseSideModal from "../BaseSideModal";
import DaysThreshold from "./components/DaysThreshold";
import InformationWrapper from "./components/InformationWrapper";

class InactiveUsersModal extends BaseSideModal {
  headerProps = {
    messageId: "inactiveUsersTitle",
    dataTestIds: {
      title: "lbl_inactive_users_sidemodal_title",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_inactive_users";

  get content() {
    return (
      <InformationWrapper>
        <DaysThreshold
          messageId={"thresholds.inactiveUsers"}
          recommendationType={this.payload?.recommendationType}
          onSuccess={this.closeSideModal}
        />
      </InformationWrapper>
    );
  }
}

export default InactiveUsersModal;

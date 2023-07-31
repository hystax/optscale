import React from "react";
import BaseSideModal from "../BaseSideModal";
import DaysThreshold from "./components/DaysThreshold";
import InformationWrapper from "./components/InformationWrapper";

class InactiveConsoleUsersModal extends BaseSideModal {
  headerProps = {
    messageId: "inactiveConsoleUsersTitle",
    dataTestIds: {
      title: "lbl_inactive_console_users_sidemodal_title",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_inactive_console_users";

  get content() {
    return (
      <InformationWrapper>
        <DaysThreshold
          messageId={"thresholds.inactiveConsoleUsers"}
          recommendationType={this.payload?.recommendationType}
          onSuccess={this.closeSideModal}
        />
      </InformationWrapper>
    );
  }
}

export default InactiveConsoleUsersModal;

import React from "react";
import BaseSideModal from "../BaseSideModal";
import DaysThreshold from "./components/DaysThreshold";
import InformationWrapper from "./components/InformationWrapper";

class NebiusMigrationModal extends BaseSideModal {
  headerProps = {
    messageId: "migrationToNebiusTitle",
    dataTestIds: {
      title: "lbl_nebius_migration_sidemodal_title",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_nebius_migration";

  get content() {
    return (
      <InformationWrapper>
        <DaysThreshold
          messageId="thresholds.nebiusMigration"
          recommendationType={this.payload?.recommendationType}
          onSuccess={this.closeSideModal}
        />
      </InformationWrapper>
    );
  }
}

export default NebiusMigrationModal;

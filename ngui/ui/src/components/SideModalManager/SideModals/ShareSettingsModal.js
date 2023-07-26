import React from "react";
import PoolLabel from "components/PoolLabel";
import ShareSettingsContainer from "containers/ShareSettingsContainer";
import BaseSideModal from "./BaseSideModal";

class ShareSettingsModal extends BaseSideModal {
  get headerProps() {
    const purpose = this.payload?.poolPurpose;

    return {
      messageId: "poolExpensesShareSettingsTitle",
      formattedMessageValues: {
        title: purpose ? (
          <PoolLabel disableLink type={purpose} name={this.payload?.poolName} iconProps={{ color: "white" }} />
        ) : null
      },
      dataTestIds: {
        title: "lbl_share_pool",
        closeButton: "btn_close"
      }
    };
  }

  dataTestId = "smodal_share_pool";

  get content() {
    const { poolId, poolName, poolPurpose, initialLink } = this.payload;

    return <ShareSettingsContainer poolId={poolId} poolName={poolName} poolPurpose={poolPurpose} initialLink={initialLink} />;
  }
}

export default ShareSettingsModal;

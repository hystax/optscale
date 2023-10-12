import React from "react";
import { CreatePoolForm } from "components/PoolForm";
import BaseSideModal from "./BaseSideModal";

class AddPoolModal extends BaseSideModal {
  get headerProps() {
    return {
      messageId: "addPoolToTitle",
      formattedMessageValues: {
        poolName: this.payload?.parentPoolName
      },
      color: "success",
      dataTestIds: {
        title: "lbl_add_pool",
        closeButton: "bnt_close"
      }
    };
  }

  dataTestId = "smodal_add_pool";

  get content() {
    return (
      <CreatePoolForm
        parentId={this.payload?.parentId}
        onSuccess={this.closeSideModal}
        unallocatedLimit={this.payload?.unallocatedLimit}
      />
    );
  }
}

export default AddPoolModal;

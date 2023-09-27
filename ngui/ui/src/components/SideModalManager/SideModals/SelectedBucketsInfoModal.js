import React from "react";
import SelectedBucketsInfo from "components/S3DuplicateFinderCheck/components/SelectedBucketsInfo";
import BaseSideModal from "./BaseSideModal";

class SelectedBucketsInfoModal extends BaseSideModal {
  headerProps = {
    messageId: "crossBucketDuplicatesTitle",
    dataTestIds: {
      title: "lbl_cross_buckets",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_cross_buckets";

  get content() {
    return (
      <SelectedBucketsInfo
        onClose={this.closeSideModal}
        fromBucket={this.payload?.fromBucket}
        toBucket={this.payload?.toBucket}
        crossBucketsStats={this.payload?.crossBucketsStats}
        checkId={this.payload?.checkId}
      />
    );
  }
}

export default SelectedBucketsInfoModal;

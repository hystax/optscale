import BaseSideModal from "../BaseSideModal";
import DaysThreshold from "./components/DaysThreshold";
import InformationWrapper from "./components/InformationWrapper";

/**
 * @deprecated OSN-1266.
 * `ObsoleteImagesModal` is deprecated because `ObsoleteImages` was replaced with `SnapshotsWithNonUsedImages`.
 */

class ObsoleteImagesModal extends BaseSideModal {
  headerProps = {
    messageId: "obsoleteImagesTitle",
    dataTestIds: {
      title: "lbl_obsolete_images_sidemodal_title",
      closeButton: "btn_close",
    },
  };

  dataTestId = "smodal_obsolete_images";

  get content() {
    return (
      <InformationWrapper>
        <DaysThreshold
          messageId="thresholds.obsoleteImages"
          recommendationType={this.payload?.recommendationType}
          onSuccess={this.closeSideModal}
        />
      </InformationWrapper>
    );
  }
}

export default ObsoleteImagesModal;

import BaseSideModal from "../BaseSideModal";
import DaysThreshold from "./components/DaysThreshold";

class AbandonedImagesModal extends BaseSideModal {
  headerProps = {
    messageId: "abandonedImages",
    dataTestIds: {
      title: "lbl_abandoned_images_sidemodal_title",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_abandoned_images_strategy";

  get content() {
    return (
      <DaysThreshold
        messageId={"thresholds.abandonedImages"}
        recommendationType={this.payload?.recommendationType}
        onSuccess={this.closeSideModal}
      />
    );
  }
}

export default AbandonedImagesModal;

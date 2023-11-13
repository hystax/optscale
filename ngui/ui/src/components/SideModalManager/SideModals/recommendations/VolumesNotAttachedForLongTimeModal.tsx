import BaseSideModal from "../BaseSideModal";
import DaysThreshold from "./components/DaysThreshold";
import InformationWrapper from "./components/InformationWrapper";

class VolumesNotAttachedForLongTimeModal extends BaseSideModal {
  headerProps = {
    messageId: "volumesNotAttachedForLongTime",
    dataTestIds: {
      title: "lbl_volumes_not_attached_for_long_time_sidemodal_title",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_volumes_not_attached_for_long_time";

  get content() {
    return (
      <InformationWrapper>
        <DaysThreshold
          messageId={"thresholds.volumesNotAttached"}
          recommendationType={this.payload?.recommendationType}
          onSuccess={this.closeSideModal}
        />
      </InformationWrapper>
    );
  }
}

export default VolumesNotAttachedForLongTimeModal;

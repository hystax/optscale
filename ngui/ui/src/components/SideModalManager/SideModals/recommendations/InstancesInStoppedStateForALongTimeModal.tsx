import BaseSideModal from "../BaseSideModal";
import DaysThreshold from "./components/DaysThreshold";
import InformationWrapper from "./components/InformationWrapper";

class InstancesInStoppedStateForALongTimeModal extends BaseSideModal {
  headerProps = {
    messageId: "instancesInStoppedStateForALongTime",
    dataTestIds: {
      title: "lbl_instances_in_stopped_state_for_a_long_time_sidemodal_title",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_instances_in_stopped_state_for_a_long_time";

  get content() {
    return (
      <InformationWrapper>
        <DaysThreshold
          messageId={"thresholds.instancesInStoppedStateForALongTime"}
          recommendationType={this.payload?.recommendationType}
          onSuccess={this.closeSideModal}
        />
      </InformationWrapper>
    );
  }
}

export default InstancesInStoppedStateForALongTimeModal;

import BaseSideModal from "../BaseSideModal";
import DaysThreshold from "./components/DaysThreshold";
import InformationWrapper from "./components/InformationWrapper";

class AbandonedKinesisStreamsModal extends BaseSideModal {
  headerProps = {
    messageId: "abandonedKinesisStreams",
    dataTestIds: {
      title: "lbl_abandoned_kinesis_streams_sidemodal_title",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_abandoned_kinesis_streams";

  get content() {
    return (
      <InformationWrapper>
        <DaysThreshold
          messageId={"thresholds.abandonedKinesisStreams"}
          recommendationType={this.payload?.recommendationType}
          onSuccess={this.closeSideModal}
        />
      </InformationWrapper>
    );
  }
}

export default AbandonedKinesisStreamsModal;

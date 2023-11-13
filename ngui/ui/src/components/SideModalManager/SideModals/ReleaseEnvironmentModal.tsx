import ReleaseBookingContainer from "containers/ReleaseBookingContainer";
import BaseSideModal from "./BaseSideModal";

class ReleaseEnvironmentModal extends BaseSideModal {
  headerProps = {
    messageId: "releaseBookingTitle",
    dataTestIds: {
      title: "lbl_release_booking",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_release_booking";

  get content() {
    return (
      <ReleaseBookingContainer
        bookingId={this.payload?.bookingId}
        onSuccess={this.closeSideModal}
        onCancel={this.closeSideModal}
      />
    );
  }
}

export default ReleaseEnvironmentModal;

import ConnectGoogleCalendarContainer from "containers/ConnectGoogleCalendarContainer";
import BaseSideModal from "./BaseSideModal";

class ConnectGoogleCalendarModal extends BaseSideModal {
  headerProps = {
    messageId: "connectGoogleCalendar",
    dataTestIds: {
      title: "lbl_connect",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_connect_google_calendar";

  get content() {
    return <ConnectGoogleCalendarContainer serviceAccount={this.payload?.serviceAccount} onCancel={this.closeSideModal} />;
  }
}

export default ConnectGoogleCalendarModal;

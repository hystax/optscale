import UnmarkEnvironmentContainer from "containers/UnmarkEnvironmentContainer";
import BaseSideModal from "./BaseSideModal";

class UnmarkEnvironmentModal extends BaseSideModal {
  headerProps = {
    messageId: "unmarkEnvironment",
    color: "error",
    dataTestIds: {
      title: "lbl_unmark",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_unmark_environment";

  get content() {
    return (
      <UnmarkEnvironmentContainer
        resourceName={this.payload?.name}
        resourceId={this.payload?.id}
        closeSideModal={this.closeSideModal}
      />
    );
  }
}

export default UnmarkEnvironmentModal;

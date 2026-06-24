import PowerByTagsContainer from "containers/PowerByTagsContainer";
import BaseSideModal from "./BaseSideModal";

class PowerByTagsModal extends BaseSideModal {
  headerProps = {
    messageId: "powerByTagsTitle",
    dataTestIds: {
      title: "lbl_power_by_tags_title",
      closeButton: "btn_close",
    },
  };

  dataTestId = "smodal_power_by_tags";

  get content() {
    return <PowerByTagsContainer handleClose={this.closeSideModal} />;
  }
}

export default PowerByTagsModal;

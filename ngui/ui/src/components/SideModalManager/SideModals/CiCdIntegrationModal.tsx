import EnvironmentCiCdIntegration from "components/EnvironmentCiCdIntegration";
import BaseSideModal from "./BaseSideModal";

class CiCdIntegrationModal extends BaseSideModal {
  headerProps = {
    messageId: "cicdIntegrationTitle",
    dataTestIds: {
      title: "lbl_assign",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_cicdintegration";

  get content() {
    return <EnvironmentCiCdIntegration text={this.payload?.envPropertiesCollectorLink || ""} />;
  }
}

export default CiCdIntegrationModal;

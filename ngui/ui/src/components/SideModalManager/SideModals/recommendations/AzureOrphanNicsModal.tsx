import { FormattedMessage } from "react-intl";
import BaseSideModal from "../BaseSideModal";
import InformationWrapper from "./components/InformationWrapper";

class AzureOrphanNicsModal extends BaseSideModal {
  headerProps = {
    messageId: "azureOrphanNicsTitle",
    dataTestIds: {
      title: "lbl_azure_orphan_nics_sidemodal_title",
      closeButton: "btn_close",
    },
  };

  dataTestId = "smodal_azure_orphan_nics";

  get content() {
    return (
      <InformationWrapper>
        <FormattedMessage id="azureOrphanNicsDescription" />
      </InformationWrapper>
    );
  }
}

export default AzureOrphanNicsModal;

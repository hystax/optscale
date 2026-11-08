import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import BaseSideModal from "../BaseSideModal";
import InformationWrapper from "./components/InformationWrapper";

const AzureColdTierCandidatesDescription = () => (
  <Typography component="div">
    <FormattedMessage id="azureColdTierCandidatesDescription" />
  </Typography>
);

class AzureColdTierCandidatesModal extends BaseSideModal {
  headerProps = {
    messageId: "azureColdTierCandidatesTitle",
    dataTestIds: {
      title: "lbl_azure_cold_tier_candidates_sidemodal_title",
      closeButton: "btn_close",
    },
  };

  dataTestId = "smodal_azure_cold_tier_candidates";

  get content() {
    return (
      <InformationWrapper>
        <AzureColdTierCandidatesDescription />
      </InformationWrapper>
    );
  }
}

export default AzureColdTierCandidatesModal;

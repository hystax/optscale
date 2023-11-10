import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import S3DuplicateFinderSettingsFormContainer from "containers/S3DuplicateFinderSettingsFormContainer";
import BaseSideModal from "./BaseSideModal";

class S3DuplicateFinderSettingsModal extends BaseSideModal {
  headerProps = {
    messageId: "settings",
    dataTestIds: {
      title: "lbl_settings",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_settings";

  get content() {
    return (
      <>
        <Typography gutterBottom>
          <FormattedMessage id="s3DuplicatesThresholdsSettingsDescription" />
        </Typography>
        <S3DuplicateFinderSettingsFormContainer closeSideModal={this.closeSideModal} />
      </>
    );
  }
}

export default S3DuplicateFinderSettingsModal;

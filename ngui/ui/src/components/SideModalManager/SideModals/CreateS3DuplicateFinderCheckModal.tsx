import CreateS3DuplicateFinderCheckContainer from "containers/CreateS3DuplicateFinderCheckContainer";
import BaseSideModal from "./BaseSideModal";

class CreateS3DuplicateFinderCheckModal extends BaseSideModal {
  headerProps = {
    messageId: "createS3DuplicateFinderCheckTitle",
    dataTestIds: {
      title: "title_create_s3_duplicate_finder_check",
      closeButton: "close_btn"
    }
  };

  dataTestId = "smodal_create_s3_duplicate_finder_check";

  get content() {
    return <CreateS3DuplicateFinderCheckContainer handleClose={this.closeSideModal} />;
  }
}

export default CreateS3DuplicateFinderCheckModal;

import React from "react";
import DeletePropertyContainer from "containers/DeletePropertyContainer";
import BaseSideModal from "./BaseSideModal";

// TODO: remove dynamic value from title, add "are you sure question"
class DeleteEnvironmentPropertyModal extends BaseSideModal {
  get headerProps() {
    return {
      messageId: "deletePropertyTitle",
      formattedMessageValues: {
        name: this.payload?.propertyName
      },
      color: "error",
      dataTestIds: {
        title: "lbl_delete_property",
        closeButton: "bnt_close"
      }
    };
  }

  dataTestId = "smodal_delete_env_property";

  get content() {
    return (
      <DeletePropertyContainer
        environmentId={this.payload?.environmentId}
        propertyName={this.payload?.propertyName}
        onSuccess={this.closeSideModal}
        onCancel={this.closeSideModal}
      />
    );
  }
}

export default DeleteEnvironmentPropertyModal;

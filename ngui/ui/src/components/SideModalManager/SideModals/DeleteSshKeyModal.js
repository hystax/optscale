import React from "react";
import DeleteSshKeyContainer from "containers/DeleteSshKeyContainer";
import BaseSideModal from "./BaseSideModal";

// TODO: remove dynamic value from title, add "are you sure question"
class DeleteSshKeyModal extends BaseSideModal {
  getCurrentKeyDefinition() {
    return this.payload?.sshKeys.find(({ id }) => id === this.payload?.keyToDeleteId) || {};
  }

  get headerProps() {
    const { name: keyName } = this.getCurrentKeyDefinition();

    return {
      messageId: "deleteSshKeyTitle",
      color: "error",
      formattedMessageValues: { value: keyName },
      dataTestIds: {
        title: "lbl_delete_cluster_type",
        closeButton: "btn_close"
      }
    };
  }

  dataTestId = "smodal_delete";

  get content() {
    const { default: isDefault } = this.getCurrentKeyDefinition();
    return (
      <DeleteSshKeyContainer
        keys={this.payload?.sshKeys}
        currentKeyId={this.payload?.keyToDeleteId}
        isDefault={isDefault}
        closeSideModal={this.closeSideModal}
      />
    );
  }
}

export default DeleteSshKeyModal;

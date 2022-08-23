import React from "react";
import PropTypes from "prop-types";
import CreateSshKey from "components/CreateSshKey";
import SshKeysTable from "components/SshKeysTable";

const SshSettings = ({
  loadingProps: { isGetSshKeysLoading = false, isCreateKeyLoading = false, isMakeDefaultLoading = false } = {},
  sshKeys = [],
  onCreateKeySubmit,
  onMakeDefault
}) => (
  <>
    <CreateSshKey onSubmit={onCreateKeySubmit} isSubmitLoading={isCreateKeyLoading} />
    <SshKeysTable
      sshKeys={sshKeys}
      isLoading={isGetSshKeysLoading}
      isMakeDefaultLoading={isMakeDefaultLoading}
      onMakeDefault={onMakeDefault}
    />
  </>
);

SshSettings.propTypes = {
  loadingProps: PropTypes.shape({
    isGetSshKeysLoading: PropTypes.bool,
    isCreateKeyLoading: PropTypes.bool,
    isMakeDefaultLoading: PropTypes.bool
  }),
  sshKeys: PropTypes.array,
  onCreateKeySubmit: PropTypes.func,
  onMakeDefault: PropTypes.func
};

export default SshSettings;

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

export default SshSettings;

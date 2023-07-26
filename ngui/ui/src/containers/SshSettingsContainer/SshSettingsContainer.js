import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { getSshKeys, createSshKey, updateSshKey } from "api";
import { GET_CURRENT_EMPLOYEE, GET_SSH_KEYS } from "api/restapi/actionTypes";
import SshSettings from "components/SshSettings";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";

const SshSettingsContainer = () => {
  const dispatch = useDispatch();

  // employee id
  const { apiData: { currentEmployee: { id: currentEmployeeId } = {} } = {} } = useApiData(GET_CURRENT_EMPLOYEE);

  // get ssh keys
  const { shouldInvoke, isLoading: isGetSshKeysLoading } = useApiState(GET_SSH_KEYS, currentEmployeeId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getSshKeys(currentEmployeeId));
    }
  }, [dispatch, currentEmployeeId, shouldInvoke]);

  const { apiData: sshKeys } = useApiData(GET_SSH_KEYS, []);

  // key creation
  const [isCreateKeyLoading, setIsCreateKeyLoading] = useState(false);
  const onCreateKeySubmit = (formData) => {
    setIsCreateKeyLoading(true);
    dispatch(createSshKey(currentEmployeeId, formData)).then(() => setIsCreateKeyLoading(false));
  };

  // make default
  const [isMakeDefaultLoading, setIsMakeDefaultLoading] = useState(false);
  const onMakeDefault = (newDefaultKeyId) => {
    // TODO: do not reload whole table after changing default key (while GET_SSH_KEYS is loading)
    setIsMakeDefaultLoading(true);
    dispatch(updateSshKey(newDefaultKeyId, { default: true })).then(() => setIsMakeDefaultLoading(false));
  };

  return (
    <SshSettings
      loadingProps={{ isGetSshKeysLoading, isCreateKeyLoading, isMakeDefaultLoading }}
      sshKeys={sshKeys}
      onCreateKeySubmit={onCreateKeySubmit}
      onMakeDefault={onMakeDefault}
    />
  );
};

SshSettingsContainer.propTypes = {};

export default SshSettingsContainer;

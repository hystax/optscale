import { useState } from "react";
import { CircularProgress, FormControl } from "@mui/material";
import { useIntl } from "react-intl";
import ButtonGroup from "components/ButtonGroup";
import { Selector } from "components/forms/common/fields";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import { ItemContent } from "components/Selector";
import { isEmpty } from "utils/arrays";
import CreateSshKeyNameField from "./CreateSshKeyNameField";
import CreateSshKeyValueField from "./CreateSshKeyValueField";

const MY_KEYS = "myKeys";
const ADD_KEY = "addKey";

export const SELECTED_KEY_FIELD_ID = "selectedKeyId";

type EnvironmentSshKeyProps = {
  sshKeys: {
    id: string;
    name: string;
    fingerprint: string;
  }[];
  isGetSshKeysReady: boolean;
  defaultKeyId: string;
};

const EnvironmentSshKeyField = ({ sshKeys = [], isGetSshKeysReady, defaultKeyId }: EnvironmentSshKeyProps) => {
  const intl = useIntl();
  const userHaveSshKeys = !isEmpty(sshKeys);
  const [activeTab, setActiveTab] = useState(userHaveSshKeys ? MY_KEYS : ADD_KEY);

  const defaultKeyText = `[${intl.formatMessage({ id: "default" }).toLowerCase()}]`;

  const activeTabIndex = activeTab === MY_KEYS ? 0 : 1;

  const buttons = [
    {
      id: MY_KEYS,
      messageId: MY_KEYS,
      action: () => setActiveTab(MY_KEYS),
      dataTestId: `tab_${MY_KEYS}`,
      disabled: !userHaveSshKeys,
      tooltip: !userHaveSshKeys && "youHaveNotCreateAnySshKeys"
    },
    {
      id: ADD_KEY,
      messageId: ADD_KEY,
      action: () => setActiveTab(ADD_KEY),
      dataTestId: `tab_${ADD_KEY}`
    }
  ];

  return !isGetSshKeysReady ? (
    <CircularProgress />
  ) : (
    <>
      <FormControl>
        <ButtonGroup buttons={buttons} activeButtonIndex={activeTabIndex} />
      </FormControl>
      {activeTab === MY_KEYS && (
        <Selector
          id="environment-ssh-key-selector"
          name={SELECTED_KEY_FIELD_ID}
          defaultValue={defaultKeyId}
          required
          labelMessageId="sshKeyForBooking"
          fullWidth
          items={sshKeys.map(({ id, name, fingerprint }) => ({
            value: id,
            content: <ItemContent>{`${name} (${fingerprint}) ${defaultKeyId === id ? defaultKeyText : ""}`}</ItemContent>
          }))}
        />
      )}
      {activeTab === ADD_KEY && (
        <>
          <InlineSeverityAlert messageDataTestId="ssh-hint" messageId="sshHint" />
          <CreateSshKeyNameField />
          <CreateSshKeyValueField />
        </>
      )}
    </>
  );
};

export default EnvironmentSshKeyField;

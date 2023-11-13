import { useState, useMemo } from "react";
import { CircularProgress } from "@mui/material";
import Grid from "@mui/material/Grid";
import { useFormContext, Controller } from "react-hook-form";
import { useIntl } from "react-intl";
import ButtonGroup from "components/ButtonGroup";
import CreateSshKeyNameField from "components/CreateSshKeyNameField";
import CreateSshKeyValueField from "components/CreateSshKeyValueField";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import Selector from "components/Selector";
import { isEmpty } from "utils/arrays";

const MY_KEYS = "myKeys";
const ADD_KEY = "addKey";

export const SELECTED_KEY_FIELD_ID = "selectedKeyId";

const buildSshKeysSelectorData = (keys, defaultKeyId, defaultKeyText) =>
  keys.map(({ id, name, fingerprint }) => ({
    name: `${name} (${fingerprint}) ${defaultKeyId === id ? defaultKeyText : ""}`,
    value: id
  }));

const EnvironmentSshKey = ({ sshKeys = [], isGetSshKeysReady, defaultKeyId }) => {
  const intl = useIntl();
  const methods = useFormContext();
  const userHaveSshKeys = !isEmpty(sshKeys);
  const [activeTab, setActiveTab] = useState(userHaveSshKeys ? MY_KEYS : ADD_KEY);

  const defaultKeyText = `[${intl.formatMessage({ id: "default" }).toLowerCase()}]`;

  const selectorData = useMemo(
    () => ({ items: buildSshKeysSelectorData(sshKeys, defaultKeyId, defaultKeyText) }),
    [sshKeys, defaultKeyId, defaultKeyText]
  );

  const {
    control,
    formState: { errors }
  } = methods;

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
      <Grid item>
        <ButtonGroup buttons={buttons} activeButtonIndex={activeTabIndex} />
      </Grid>
      {activeTab === MY_KEYS && (
        <Controller
          name={SELECTED_KEY_FIELD_ID}
          control={control}
          rules={{
            required: {
              value: true,
              message: intl.formatMessage({ id: "thisFieldIsRequired" })
            }
          }}
          defaultValue={defaultKeyId}
          render={({ field }) => (
            <Selector
              required
              error={!!errors[SELECTED_KEY_FIELD_ID]}
              helperText={errors?.[SELECTED_KEY_FIELD_ID]?.message}
              data={selectorData}
              labelId="sshKeyForBooking"
              {...field}
            />
          )}
        />
      )}
      {activeTab === ADD_KEY && (
        <>
          <Grid item xs={12}>
            <InlineSeverityAlert messageDataTestId="ssh-hint" messageId="sshHint" />
          </Grid>
          <CreateSshKeyNameField />
          <CreateSshKeyValueField />
        </>
      )}
    </>
  );
};

export default EnvironmentSshKey;

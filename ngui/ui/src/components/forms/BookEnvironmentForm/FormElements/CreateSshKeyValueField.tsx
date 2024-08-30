import { useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.KEY_VALUE;

const CreateSshKeyValueField = () => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      required
      /**
       *  Unregister the field to exclude it from the form state when
       *  booking for user other users (not for myself)
       */
      shouldUnregister
      label={intl.formatMessage({ id: "value" })}
      multiline
      rows={4}
      placeholder={intl.formatMessage({ id: "sshKeyPlaceholder" })}
      dataTestId="input_new_key_value"
    />
  );
};

export default CreateSshKeyValueField;

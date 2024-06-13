import { useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.KEY_NAME;

const CreateSshKeyNameField = () => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      /**
       *  Unregister the field to exclude it from the form state when
       *  booking for user other users (not for myself)
       */
      shouldUnregister
      required
      label={intl.formatMessage({ id: "name" })}
      placeholder={intl.formatMessage({ id: "sshNamePlaceholder" })}
      dataTestId="input_new_key_title"
    />
  );
};

export default CreateSshKeyNameField;

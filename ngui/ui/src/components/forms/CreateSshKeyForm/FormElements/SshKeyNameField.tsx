import { FormattedMessage, useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.KEY_NAME;

const SshKeyNameField = () => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      label={<FormattedMessage id="name" />}
      required
      dataTestId="input_new_key_title"
      placeholder={intl.formatMessage({ id: "sshNamePlaceholder" })}
    />
  );
};

export default SshKeyNameField;

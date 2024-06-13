import { FormattedMessage, useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.KEY_VALUE;

const SshKeyValueField = () => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      label={<FormattedMessage id="value" />}
      placeholder={intl.formatMessage({ id: "sshKeyPlaceholder" })}
      required
      multiline
      rows={4}
      maxLength={null}
      dataTestId="input_new_key_value"
    />
  );
};

export default SshKeyValueField;

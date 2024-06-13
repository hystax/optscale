import { FormattedMessage, useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES, MAX_INPUT_LENGTH } from "../constants";

const FIELD_NAME = FIELD_NAMES.MISSING_CAPABILITIES;

const MissingCapabilitiesField = () => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      label={<FormattedMessage id="capabilitiesQuestion" />}
      placeholder={intl.formatMessage(
        { id: "maxLength" },
        { inputName: intl.formatMessage({ id: "answer" }), max: MAX_INPUT_LENGTH }
      )}
      rows={4}
      multiline
      maxLength={MAX_INPUT_LENGTH}
    />
  );
};

export default MissingCapabilitiesField;

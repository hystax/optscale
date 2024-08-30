import { FormattedMessage, useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { DEFAULT_MAX_TEXTAREA_LENGTH } from "utils/constants";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.DESCRIPTION;

const MlEditTaskFormDescriptionField = () => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      dataTestId="input_description"
      label={<FormattedMessage id="description" />}
      minRows={6}
      maxRows={16}
      multiline
      placeholder={intl.formatMessage({ id: "markdownIsSupported" })}
      maxLength={DEFAULT_MAX_TEXTAREA_LENGTH}
    />
  );
};

export default MlEditTaskFormDescriptionField;

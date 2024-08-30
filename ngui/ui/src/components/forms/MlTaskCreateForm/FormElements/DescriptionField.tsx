import { FormattedMessage, useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { DEFAULT_MAX_TEXTAREA_LENGTH } from "utils/constants";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.DESCRIPTION;

const DescriptionField = () => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      label={<FormattedMessage id="description" />}
      placeholder={intl.formatMessage({ id: "markdownIsSupported" })}
      minRows={6}
      maxRows={16}
      maxLength={DEFAULT_MAX_TEXTAREA_LENGTH}
      multiline
      dataTestId="input_description"
    />
  );
};

export default DescriptionField;

import { FormattedMessage, useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { DEFAULT_MAX_TEXTAREA_LENGTH } from "utils/constants";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.DESCRIPTION;

const DescriptionField = ({ isLoading = false }) => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      label={<FormattedMessage id="description" />}
      required
      minRows={6}
      maxRows={16}
      multiline
      maxLength={DEFAULT_MAX_TEXTAREA_LENGTH}
      placeholder={intl.formatMessage({ id: "markdownIsSupported" })}
      isLoading={isLoading}
      dataTestId="input_description"
    />
  );
};

export default DescriptionField;

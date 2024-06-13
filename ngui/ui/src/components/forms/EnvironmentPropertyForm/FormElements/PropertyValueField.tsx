import { FormattedMessage, useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { DEFAULT_MAX_TEXTAREA_LENGTH } from "utils/constants";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.PROPERTY_VALUE;

const PropertyValueField = () => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      label={<FormattedMessage id="value" />}
      required
      maxLength={DEFAULT_MAX_TEXTAREA_LENGTH}
      rows={4}
      multiline
      placeholder={intl.formatMessage({ id: "markdownIsSupported" })}
    />
  );
};

export default PropertyValueField;

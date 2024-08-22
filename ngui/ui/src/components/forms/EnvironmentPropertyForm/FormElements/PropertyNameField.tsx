import { FormattedMessage, useIntl } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { ENVIRONMENT_PROPERTY_NAME_MAX_INPUT_LENGTH } from "utils/constants";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.PROPERTY_NAME;

const PropertyNameField = ({ readOnly, defaultPropertyName, existingProperties }) => {
  const intl = useIntl();

  return (
    <TextInput
      name={FIELD_NAME}
      label={<FormattedMessage id="name" />}
      required
      InputProps={{ readOnly }}
      maxLength={ENVIRONMENT_PROPERTY_NAME_MAX_INPUT_LENGTH}
      validate={{
        unique: (value) => {
          const propertyAlreadyExists = Object.keys(existingProperties).some(
            (existingPropertyName) => defaultPropertyName !== existingPropertyName && value === existingPropertyName
          );

          return !propertyAlreadyExists || intl.formatMessage({ id: "propertyNamesMustBeUnique" });
        }
      }}
    />
  );
};

export default PropertyNameField;

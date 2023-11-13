import { FormattedMessage } from "react-intl";
import Input from "components/Input";
import { intl } from "translations/react-intl-config";
import { ENVIRONMENT_PROPERTY_NAME_MAX_INPUT_LENGTH } from "utils/constants";

const EnvironmentPropertyNameInput = ({ name, register, error, helperText, readOnly = false, validate, dataTestId }) => (
  <Input
    label={!readOnly && <FormattedMessage id="name" />}
    required
    error={error}
    InputProps={{ readOnly }}
    helperText={helperText}
    {...register(name, {
      required: {
        value: true,
        message: intl.formatMessage({ id: "thisFieldIsRequired" })
      },
      maxLength: {
        value: ENVIRONMENT_PROPERTY_NAME_MAX_INPUT_LENGTH,
        message: intl.formatMessage(
          { id: "maxLength" },
          { inputName: intl.formatMessage({ id: "propertyName" }), max: ENVIRONMENT_PROPERTY_NAME_MAX_INPUT_LENGTH }
        )
      },
      validate
    })}
    dataTestId={dataTestId}
  />
);

export default EnvironmentPropertyNameInput;

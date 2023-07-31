import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { ENVIRONMENT_PROPERTY_VALUE_MAX_INPUT_LENGTH } from "utils/constants";

const EnvironmentPropertyValueInput = ({ name, register, error, helperText, dataTestId }) => {
  const intl = useIntl();

  return (
    <Input
      label={<FormattedMessage id="value" />}
      required
      error={error}
      helperText={helperText}
      {...register(name, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: {
          value: ENVIRONMENT_PROPERTY_VALUE_MAX_INPUT_LENGTH,
          message: intl.formatMessage(
            { id: "maxLength" },
            { inputName: intl.formatMessage({ id: "propertyValue" }), max: ENVIRONMENT_PROPERTY_VALUE_MAX_INPUT_LENGTH }
          )
        }
      })}
      rows={4}
      multiline
      placeholder={intl.formatMessage({ id: "propertyValuePlaceholder" })}
      dataTestId={dataTestId}
    />
  );
};

EnvironmentPropertyValueInput.propTypes = {
  name: PropTypes.string.isRequired,
  register: PropTypes.func.isRequired,
  error: PropTypes.bool,
  helperText: PropTypes.string,
  dataTestId: PropTypes.string
};

export default EnvironmentPropertyValueInput;

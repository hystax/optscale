import React from "react";
import PropTypes from "prop-types";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";

const MlModelCreateFormNameField = ({ name }) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <Input
      margin="normal"
      dataTestId="input_name"
      label={<FormattedMessage id="name" />}
      required
      autoFocus
      error={!!errors[name]}
      helperText={errors[name] && errors[name].message}
      {...register(name, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: {
          value: DEFAULT_MAX_INPUT_LENGTH,
          message: intl.formatMessage(
            { id: "maxLength" },
            { inputName: intl.formatMessage({ id: "name" }), max: DEFAULT_MAX_INPUT_LENGTH }
          )
        }
      })}
    />
  );
};

MlModelCreateFormNameField.propTypes = {
  name: PropTypes.string.isRequired
};

export default MlModelCreateFormNameField;

import React from "react";
import PropTypes from "prop-types";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";

const OrganizationOptionNameInput = ({ name }) => {
  const intl = useIntl();
  const {
    register,
    formState: { errors }
  } = useFormContext();

  return (
    <Input
      margin="none"
      required
      error={!!errors[name]}
      helperText={errors[name]?.message}
      label={<FormattedMessage id="name" />}
      {...register(name, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: {
          value: DEFAULT_MAX_INPUT_LENGTH,
          message: intl.formatMessage(
            { id: "maxLength" },
            {
              inputName: intl.formatMessage(
                { id: "entity:name" },
                { entity: intl.formatMessage({ id: "organizationOption" }) }
              ),
              max: DEFAULT_MAX_INPUT_LENGTH
            }
          )
        }
      })}
    />
  );
};

OrganizationOptionNameInput.propTypes = {
  name: PropTypes.string.isRequired
};

export default OrganizationOptionNameInput;

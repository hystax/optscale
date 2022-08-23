import React from "react";
import PropTypes from "prop-types";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { MAX_ORGANIZATION_NAME_LENGTH } from "utils/constants";

const OrganizationNameInput = ({ name }) => {
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
          value: MAX_ORGANIZATION_NAME_LENGTH,
          message: intl.formatMessage(
            { id: "maxLength" },
            {
              inputName: intl.formatMessage({ id: "entity:name" }, { entity: intl.formatMessage({ id: "organization" }) }),
              max: MAX_ORGANIZATION_NAME_LENGTH
            }
          )
        }
      })}
    />
  );
};

OrganizationNameInput.propTypes = {
  name: PropTypes.string.isRequired
};

export default OrganizationNameInput;

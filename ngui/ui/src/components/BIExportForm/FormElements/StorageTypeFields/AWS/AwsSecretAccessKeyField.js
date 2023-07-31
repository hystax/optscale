import React from "react";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";
import { notOnlyWhiteSpaces } from "utils/validation";

export const FIELD_NAME = "awsSecretAccessKey";

const AwsSecretAccessKeyField = ({ isLoading }) => {
  const intl = useIntl();

  const {
    register,
    formState: { errors }
  } = useFormContext();

  return isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <Input
      required
      isMasked
      dataTestId="input_aws_secret_key"
      error={!!errors[FIELD_NAME]}
      helperText={errors[FIELD_NAME] && errors[FIELD_NAME].message}
      label={<FormattedMessage id="awsSecretAccessKey" />}
      autoComplete="off"
      {...register(FIELD_NAME, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: {
          value: DEFAULT_MAX_INPUT_LENGTH,
          message: intl.formatMessage(
            { id: "maxLength" },
            { inputName: intl.formatMessage({ id: "awsSecretAccessKey" }), max: DEFAULT_MAX_INPUT_LENGTH }
          )
        },
        validate: {
          notOnlyWhiteSpaces
        }
      })}
    />
  );
};

export default AwsSecretAccessKeyField;

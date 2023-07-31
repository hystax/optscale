import React from "react";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import PasswordInput from "components/PasswordInput";
import QuestionMark from "components/QuestionMark";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";

export const FIELD_NAMES = Object.freeze({
  PASSWORD: "password",
  USER: "user"
});

const KubernetesCredentials = () => {
  const intl = useIntl();

  const {
    register,
    formState: { errors }
  } = useFormContext();

  return (
    <>
      <Input
        required
        type="text"
        dataTestId="input_user"
        error={!!errors[FIELD_NAMES.USER]}
        helperText={errors[FIELD_NAMES.USER] && errors[FIELD_NAMES.USER].message}
        InputProps={{
          endAdornment: <QuestionMark messageId="userTooltip" dataTestId="qmark_user" />
        }}
        label={<FormattedMessage id={FIELD_NAMES.USER} />}
        {...register(FIELD_NAMES.USER, {
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          maxLength: {
            value: DEFAULT_MAX_INPUT_LENGTH,
            message: intl.formatMessage(
              { id: "maxLength" },
              { inputName: intl.formatMessage({ id: FIELD_NAMES.USER }), max: DEFAULT_MAX_INPUT_LENGTH }
            )
          }
        })}
      />
      <PasswordInput
        required
        dataTestId="input_password"
        name={FIELD_NAMES.PASSWORD}
        error={!!errors[FIELD_NAMES.PASSWORD]}
        helperText={errors[FIELD_NAMES.PASSWORD] && errors[FIELD_NAMES.PASSWORD].message}
        InputProps={{
          endAdornment: <QuestionMark messageId="passwordTooltip" dataTestId="qmark_password" />
        }}
        label={<FormattedMessage id="password" />}
        {...register(FIELD_NAMES.PASSWORD, {
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          maxLength: {
            value: DEFAULT_MAX_INPUT_LENGTH,
            message: intl.formatMessage(
              { id: "maxLength" },
              { inputName: intl.formatMessage({ id: "password" }), max: DEFAULT_MAX_INPUT_LENGTH }
            )
          }
        })}
        autoComplete="one-time-code"
      />
    </>
  );
};

export default KubernetesCredentials;

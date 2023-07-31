import React from "react";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAME = "privateKey";

const AuthorizedKeyPrivateKey = () => {
  const intl = useIntl();

  const {
    register,
    formState: { errors }
  } = useFormContext();

  return (
    <Input
      required
      dataTestId="input_nebius_private_authorized_key"
      error={!!errors[FIELD_NAME]}
      helperText={errors[FIELD_NAME] && errors[FIELD_NAME].message}
      InputProps={{
        endAdornment: (
          <QuestionMark
            messageId="nebiusPrivateAuthorizedKeyTooltip"
            messageValues={{
              i: (chunks) => <i>{chunks}</i>
            }}
            dataTestId="qmark_private_authorized_key"
          />
        )
      }}
      multiline
      minRows={4}
      label={<FormattedMessage id="privateKey" />}
      autoComplete="off"
      {...register(FIELD_NAME, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      })}
      sx={{
        marginBottom: (theme) => theme.spacing(1)
      }}
    />
  );
};

export default AuthorizedKeyPrivateKey;

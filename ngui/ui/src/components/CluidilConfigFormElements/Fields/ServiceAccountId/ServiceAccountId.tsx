import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import QuestionMark from "components/QuestionMark";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";

export const FIELD_NAME = "serviceAccountId";

const ServiceAccountId = () => {
  const intl = useIntl();

  const {
    register,
    formState: { errors }
  } = useFormContext();

  return (
    <Input
      required
      dataTestId="input_nebius_service_account_id"
      error={!!errors[FIELD_NAME]}
      helperText={errors[FIELD_NAME] && errors[FIELD_NAME].message}
      InputProps={{
        endAdornment: (
          <QuestionMark
            messageId="nebiusServiceAccountIdTooltip"
            messageValues={{
              i: (chunks) => <i>{chunks}</i>
            }}
            dataTestId="qmark_service_account_id"
          />
        )
      }}
      label={<FormattedMessage id="serviceAccountId" />}
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
            { inputName: intl.formatMessage({ id: "serviceAccountId" }), max: DEFAULT_MAX_INPUT_LENGTH }
          )
        }
      })}
      sx={{
        marginBottom: (theme) => theme.spacing(1)
      }}
    />
  );
};

export default ServiceAccountId;

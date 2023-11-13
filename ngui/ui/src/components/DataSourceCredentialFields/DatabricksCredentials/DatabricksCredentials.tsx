import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import QuestionMark from "components/QuestionMark";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";

export const FIELD_NAMES = Object.freeze({
  ACCOUNT_ID: "accountId",
  CLIENT_ID: "clientId",
  CLIENT_SECRET: "clientSecret"
});

const DatabricksCredentials = ({ readOnlyFields = [] }) => {
  const intl = useIntl();

  const {
    register,
    formState: { errors }
  } = useFormContext();

  const isReadOnly = (fieldName) => readOnlyFields.includes(fieldName);

  return (
    <>
      <Input
        required
        dataTestId="input_databricks_account_id"
        error={!!errors[FIELD_NAMES.ACCOUNT_ID]}
        helperText={errors[FIELD_NAMES.ACCOUNT_ID] && errors[FIELD_NAMES.ACCOUNT_ID].message}
        InputProps={{
          readOnly: isReadOnly(FIELD_NAMES.ACCOUNT_ID),
          endAdornment: isReadOnly(FIELD_NAMES.ACCOUNT_ID) ? null : (
            <QuestionMark
              messageId="databricksAccountIdTooltip"
              messageValues={{
                i: (chunks) => <i>{chunks}</i>
              }}
              dataTestId="qmark_tenant_id"
            />
          )
        }}
        label={<FormattedMessage id="accountId" />}
        {...register(FIELD_NAMES.ACCOUNT_ID, {
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          maxLength: {
            value: DEFAULT_MAX_INPUT_LENGTH,
            message: intl.formatMessage(
              { id: "maxLength" },
              { inputName: intl.formatMessage({ id: "accountId" }), max: DEFAULT_MAX_INPUT_LENGTH }
            )
          }
        })}
      />
      <Input
        required
        dataTestId="input_databricks_client_id"
        error={!!errors[FIELD_NAMES.CLIENT_ID]}
        helperText={errors[FIELD_NAMES.CLIENT_ID] && errors[FIELD_NAMES.CLIENT_ID].message}
        InputProps={{
          endAdornment: (
            <QuestionMark
              messageId="databricksClientIdTooltip"
              messageValues={{
                i: (chunks) => <i>{chunks}</i>
              }}
              dataTestId="qmark_access_key"
            />
          )
        }}
        label={<FormattedMessage id="clientId" />}
        {...register(FIELD_NAMES.CLIENT_ID, {
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          maxLength: {
            value: DEFAULT_MAX_INPUT_LENGTH,
            message: intl.formatMessage(
              { id: "maxLength" },
              { inputName: intl.formatMessage({ id: "clientId" }), max: DEFAULT_MAX_INPUT_LENGTH }
            )
          }
        })}
      />
      <Input
        required
        isMasked
        dataTestId="input_databricks_client_secret"
        error={!!errors[FIELD_NAMES.CLIENT_SECRET]}
        helperText={errors[FIELD_NAMES.CLIENT_SECRET] && errors[FIELD_NAMES.CLIENT_SECRET].message}
        InputProps={{
          endAdornment: (
            <QuestionMark
              messageId="databricksSecretTooltip"
              messageValues={{
                i: (chunks) => <i>{chunks}</i>
              }}
              dataTestId="qmark_access_key"
            />
          )
        }}
        label={<FormattedMessage id="clientSecret" />}
        autoComplete="off"
        {...register(FIELD_NAMES.CLIENT_SECRET, {
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          maxLength: {
            value: DEFAULT_MAX_INPUT_LENGTH,
            message: intl.formatMessage(
              { id: "maxLength" },
              { inputName: intl.formatMessage({ id: "clientSecret" }), max: DEFAULT_MAX_INPUT_LENGTH }
            )
          }
        })}
      />
    </>
  );
};

export default DatabricksCredentials;

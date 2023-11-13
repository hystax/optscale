import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import QuestionMark from "components/QuestionMark";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";

export const FIELD_NAMES = Object.freeze({
  CLIENT_ID: "clientId",
  TENANT: "tenant",
  SECRET: "secret"
});

const AzureTenantCredentials = ({ readOnlyFields = [] }) => {
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
        dataTestId="input_tenant_id"
        error={!!errors[FIELD_NAMES.TENANT]}
        helperText={errors[FIELD_NAMES.TENANT] && errors[FIELD_NAMES.TENANT].message}
        InputProps={{
          readOnly: isReadOnly(FIELD_NAMES.TENANT),
          endAdornment: isReadOnly(FIELD_NAMES.TENANT) ? null : (
            <QuestionMark
              messageId="directoryTenantIdTooltip"
              messageValues={{
                i: (chunks) => <i>{chunks}</i>
              }}
              dataTestId="qmark_tenant_id"
            />
          )
        }}
        label={<FormattedMessage id="directoryTenantId" />}
        autoComplete="off"
        {...register(FIELD_NAMES.TENANT, {
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          maxLength: {
            value: DEFAULT_MAX_INPUT_LENGTH,
            message: intl.formatMessage(
              { id: "maxLength" },
              { inputName: intl.formatMessage({ id: "directoryTenantId" }), max: DEFAULT_MAX_INPUT_LENGTH }
            )
          }
        })}
      />
      <Input
        required
        dataTestId="input_client_id"
        error={!!errors[FIELD_NAMES.CLIENT_ID]}
        helperText={errors[FIELD_NAMES.CLIENT_ID] && errors[FIELD_NAMES.CLIENT_ID].message}
        InputProps={{
          endAdornment: (
            <QuestionMark
              messageId="applicationClientIdTooltip"
              messageValues={{
                i: (chunks) => <i>{chunks}</i>
              }}
              dataTestId="qmark_client_id"
            />
          )
        }}
        label={<FormattedMessage id="applicationClientId" />}
        autoComplete="off"
        {...register(FIELD_NAMES.CLIENT_ID, {
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          maxLength: {
            value: DEFAULT_MAX_INPUT_LENGTH,
            message: intl.formatMessage(
              { id: "maxLength" },
              { inputName: intl.formatMessage({ id: "applicationClientId" }), max: DEFAULT_MAX_INPUT_LENGTH }
            )
          }
        })}
      />
      <Input
        required
        dataTestId="input_azure_secret"
        isMasked
        key={FIELD_NAMES.SECRET}
        error={!!errors[FIELD_NAMES.SECRET]}
        helperText={errors[FIELD_NAMES.SECRET] && errors[FIELD_NAMES.SECRET].message}
        InputProps={{
          endAdornment: (
            <QuestionMark
              messageId="secretTooltip"
              messageValues={{
                i: (chunks) => <i>{chunks}</i>
              }}
              dataTestId="qmark_secret"
            />
          )
        }}
        label={<FormattedMessage id={FIELD_NAMES.SECRET} />}
        autoComplete="off"
        {...register(FIELD_NAMES.SECRET, {
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          maxLength: {
            value: DEFAULT_MAX_INPUT_LENGTH,
            message: intl.formatMessage(
              { id: "maxLength" },
              { inputName: intl.formatMessage({ id: FIELD_NAMES.SECRET }), max: DEFAULT_MAX_INPUT_LENGTH }
            )
          }
        })}
      />
    </>
  );
};

export default AzureTenantCredentials;

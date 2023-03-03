import React from "react";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import QuestionMark from "components/QuestionMark";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";

export const FIELD_NAMES = Object.freeze({
  SUBSCRIPTION_ID: "subscriptionId",
  CLIENT_ID: "clientId",
  TENANT: "tenant",
  SECRET: "secret"
});

const AzureCredentials = ({ hidden = [] }) => {
  const intl = useIntl();

  const isHidden = (fieldName) => hidden.includes(fieldName);

  const {
    register,
    formState: { errors }
  } = useFormContext();

  return (
    <>
      {!isHidden(FIELD_NAMES.SUBSCRIPTION_ID) && (
        <Input
          required
          dataTestId="input_subscription_id"
          error={!!errors[FIELD_NAMES.SUBSCRIPTION_ID]}
          helperText={errors[FIELD_NAMES.SUBSCRIPTION_ID] && errors[FIELD_NAMES.SUBSCRIPTION_ID].message}
          InputProps={{
            endAdornment: <QuestionMark messageId="subscriptionIdTooltip" dataTestId="qmark_subs_id" />
          }}
          label={<FormattedMessage id={FIELD_NAMES.SUBSCRIPTION_ID} />}
          autoComplete="off"
          {...register(FIELD_NAMES.SUBSCRIPTION_ID, {
            required: {
              value: true,
              message: intl.formatMessage({ id: "thisFieldIsRequired" })
            },
            maxLength: {
              value: DEFAULT_MAX_INPUT_LENGTH,
              message: intl.formatMessage(
                { id: "maxLength" },
                { inputName: intl.formatMessage({ id: FIELD_NAMES.SUBSCRIPTION_ID }), max: DEFAULT_MAX_INPUT_LENGTH }
              )
            }
          })}
        />
      )}
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
        dataTestId="input_tenant_id"
        error={!!errors[FIELD_NAMES.TENANT]}
        helperText={errors[FIELD_NAMES.TENANT] && errors[FIELD_NAMES.TENANT].message}
        InputProps={{
          endAdornment: (
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

export default AzureCredentials;

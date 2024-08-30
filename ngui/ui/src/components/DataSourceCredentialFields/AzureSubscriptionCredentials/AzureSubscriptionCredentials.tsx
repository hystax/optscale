import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAMES = Object.freeze({
  SUBSCRIPTION_ID: "subscriptionId",
  CLIENT_ID: "clientId",
  TENANT: "tenant",
  SECRET: "secret"
});

const AzureSubscriptionCredentials = ({ hiddenFields = [], readOnlyFields = [] }) => {
  const isHidden = (fieldName) => hiddenFields.includes(fieldName);
  const isReadOnly = (fieldName) => readOnlyFields.includes(fieldName);

  return (
    <>
      <TextInput
        name={FIELD_NAMES.TENANT}
        required
        dataTestId="input_tenant_id"
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
      />
      {!isHidden(FIELD_NAMES.SUBSCRIPTION_ID) && (
        <TextInput
          name={FIELD_NAMES.SUBSCRIPTION_ID}
          required
          dataTestId="input_subscription_id"
          InputProps={{
            endAdornment: <QuestionMark messageId="subscriptionIdTooltip" dataTestId="qmark_subs_id" />
          }}
          label={<FormattedMessage id={FIELD_NAMES.SUBSCRIPTION_ID} />}
          autoComplete="off"
        />
      )}
      <TextInput
        name={FIELD_NAMES.CLIENT_ID}
        required
        dataTestId="input_client_id"
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
      />
      <TextInput
        name={FIELD_NAMES.SECRET}
        required
        masked
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
        dataTestId="input_azure_secret"
        label={<FormattedMessage id={FIELD_NAMES.SECRET} />}
        autoComplete="off"
      />
    </>
  );
};

export default AzureSubscriptionCredentials;

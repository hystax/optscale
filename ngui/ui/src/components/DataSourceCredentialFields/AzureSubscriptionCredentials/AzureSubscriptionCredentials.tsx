import { useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { Switch, TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAMES = Object.freeze({
  SUBSCRIPTION_ID: "subscriptionId",
  CLIENT_ID: "clientId",
  TENANT: "tenant",
  SECRET: "secret",
  USE_BILLING_EXPORT: "useBillingExport",
  EXPORT_NAME: "exportName",
  STORAGE_ACCOUNT_CONNECTION_STRING: "storageAccountConnectionString",
  STORAGE_CONTAINER: "storageContainer",
  STORAGE_DIRECTORY: "storageDirectory",
});

const AzureSubscriptionCredentials = ({ hiddenFields = [], readOnlyFields = [] }) => {
  const isHidden = (fieldName) => hiddenFields.includes(fieldName);
  const isReadOnly = (fieldName) => readOnlyFields.includes(fieldName);

  const { watch } = useFormContext();

  const useBillingExportEnabled = watch(FIELD_NAMES.USE_BILLING_EXPORT);

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
                i: (chunks) => <i>{chunks}</i>,
              }}
              dataTestId="qmark_tenant_id"
            />
          ),
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
            endAdornment: <QuestionMark messageId="subscriptionIdTooltip" dataTestId="qmark_subs_id" />,
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
                i: (chunks) => <i>{chunks}</i>,
              }}
              dataTestId="qmark_client_id"
            />
          ),
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
                i: (chunks) => <i>{chunks}</i>,
              }}
              dataTestId="qmark_secret"
            />
          ),
        }}
        dataTestId="input_azure_secret"
        label={<FormattedMessage id={FIELD_NAMES.SECRET} />}
        autoComplete="off"
      />
      <Switch
        name={FIELD_NAMES.USE_BILLING_EXPORT}
        label={<FormattedMessage id="useBillingExport" />}
        defaultValue={useBillingExportEnabled ?? false}
        adornment={<QuestionMark messageId="useBillingExportDescription" dataTestId="qmark_use_billing_export" />}
      />
      {useBillingExportEnabled && (
        <>
          <TextInput
            name={FIELD_NAMES.EXPORT_NAME}
            required
            InputProps={{
              endAdornment: (
                <QuestionMark
                  messageId="exportNameDescription"
                  messageValues={{
                    i: (chunks) => <i>{chunks}</i>,
                  }}
                  dataTestId="qmark_export_name"
                />
              ),
            }}
            dataTestId="input_azure_export_name"
            label={<FormattedMessage id={FIELD_NAMES.EXPORT_NAME} />}
            autoComplete="off"
          />
          <TextInput
            name={FIELD_NAMES.STORAGE_ACCOUNT_CONNECTION_STRING}
            required
            InputProps={{
              endAdornment: (
                <QuestionMark
                  messageId="storageAccountConnectionStringDescription"
                  messageValues={{
                    i: (chunks) => <i>{chunks}</i>,
                  }}
                  dataTestId="qmark_storage_account_connection_string"
                />
              ),
            }}
            masked
            dataTestId="input_azure_storage_account_connection_string"
            label={<FormattedMessage id={FIELD_NAMES.STORAGE_ACCOUNT_CONNECTION_STRING} />}
            autoComplete="off"
          />
          <TextInput
            name={FIELD_NAMES.STORAGE_CONTAINER}
            required
            InputProps={{
              endAdornment: (
                <QuestionMark
                  messageId="storageContainerDescription"
                  messageValues={{
                    i: (chunks) => <i>{chunks}</i>,
                  }}
                  dataTestId="qmark_storage_container"
                />
              ),
            }}
            dataTestId="input_azure_container"
            label={<FormattedMessage id={FIELD_NAMES.STORAGE_CONTAINER} />}
            autoComplete="off"
          />
          <TextInput
            name={FIELD_NAMES.STORAGE_DIRECTORY}
            required
            InputProps={{
              endAdornment: (
                <QuestionMark
                  messageId="storageDirectoryDescription"
                  messageValues={{
                    i: (chunks) => <i>{chunks}</i>,
                  }}
                  dataTestId="qmark_storage_directory"
                />
              ),
            }}
            dataTestId="input_azure_directory"
            label={<FormattedMessage id={FIELD_NAMES.STORAGE_DIRECTORY} />}
            autoComplete="off"
          />
        </>
      )}
    </>
  );
};

export default AzureSubscriptionCredentials;

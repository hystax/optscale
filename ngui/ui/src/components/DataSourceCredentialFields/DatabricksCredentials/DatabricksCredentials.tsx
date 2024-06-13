import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAMES = Object.freeze({
  ACCOUNT_ID: "accountId",
  CLIENT_ID: "clientId",
  CLIENT_SECRET: "clientSecret"
});

const DatabricksCredentials = ({ readOnlyFields = [] }) => {
  const isReadOnly = (fieldName) => readOnlyFields.includes(fieldName);

  return (
    <>
      <TextInput
        name={FIELD_NAMES.ACCOUNT_ID}
        required
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
        dataTestId="input_databricks_account_id"
      />
      <TextInput
        name={FIELD_NAMES.CLIENT_ID}
        required
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
        dataTestId="input_databricks_client_id"
      />
      <TextInput
        name={FIELD_NAMES.CLIENT_SECRET}
        required
        masked
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
      />
    </>
  );
};

export default DatabricksCredentials;

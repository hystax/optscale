import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAMES = Object.freeze({
  ASSUME_ROLE_ACCOUNT_ID: "awsRoleAccountId",
  ASSUME_ROLE_NAME: "awsRoleName",
});

const AwsAssumedRoleCredentials = ({ readOnlyFields = [] }: { readOnlyFields: string[] }) => {
  const isReadOnly = (fieldName: string) => readOnlyFields.includes(fieldName);

  return (
    <>
      <TextInput
        name={FIELD_NAMES.ASSUME_ROLE_ACCOUNT_ID}
        required
        dataTestId="input_assume_role_account_id"
        InputProps={{
          readOnly: isReadOnly(FIELD_NAMES.ASSUME_ROLE_ACCOUNT_ID),
          endAdornment: <QuestionMark messageId="awsRoleAccountIdTooltip" dataTestId="qmark_assume_role_id" />,
        }}
        label={<FormattedMessage id="awsRoleAccountId" />}
        autoComplete="off"
      />
      <TextInput
        name={FIELD_NAMES.ASSUME_ROLE_NAME}
        required
        dataTestId="input_assume_role_name"
        InputProps={{
          endAdornment: <QuestionMark messageId="awsRoleNameTooltip" dataTestId="qmark_assume_role_name" />,
        }}
        label={<FormattedMessage id="awsRoleName" />}
        autoComplete="off"
      />
    </>
  );
};

export default AwsAssumedRoleCredentials;

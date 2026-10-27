import { ReactNode } from "react";
import Link from "@mui/material/Link";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { v4 as uuidv4 } from "uuid";
import Button from "components/Button";
import { Switch, TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";
import { AWS_DOCS_IAM_THIRD_PARTY_ACCESS } from "urls";
import FieldWithActionButton from "../FieldWithActionButton";

export const FIELD_NAMES = Object.freeze({
  ASSUME_ROLE_ACCOUNT_ID: "awsRoleAccountId",
  ASSUME_ROLE_NAME: "awsRoleName",
  ASSUME_ROLE_EXTERNAL_ID: "awsRoleExternalId",
  USE_EXTERNAL_ID: "awsUseExternalId",
});

const EXTERNAL_ID_MIN_LENGTH = 2;
const EXTERNAL_ID_MAX_LENGTH = 1224;
const EXTERNAL_ID_PATTERN = /^[\w+=,.@:/-]*$/;

const externalIdTooltipMessageValues = {
  link: (chunks: ReactNode) => (
    <Link href={AWS_DOCS_IAM_THIRD_PARTY_ACCESS} target="_blank" rel="noopener">
      {chunks}
    </Link>
  ),
};

const ExternalIdTextInput = ({ readOnly = false }: { readOnly?: boolean }) => {
  const {
    setValue,
    formState: { errors },
  } = useFormContext();
  const intl = useIntl();

  const fieldError = errors[FIELD_NAMES.ASSUME_ROLE_EXTERNAL_ID];

  return (
    <FieldWithActionButton
      errorMessage={fieldError?.message}
      button={
        !readOnly && (
          <Button
            sx={{
              height: 40,
            }}
            messageId="generate"
            size="medium"
            color="primary"
            dataTestId="btn_generate_assume_role_external_id"
            onClick={() => setValue(FIELD_NAMES.ASSUME_ROLE_EXTERNAL_ID, uuidv4(), { shouldValidate: true })}
          />
        )
      }
    >
      <TextInput
        name={FIELD_NAMES.ASSUME_ROLE_EXTERNAL_ID}
        dataTestId="input_assume_role_external_id"
        InputProps={{
          readOnly,
          endAdornment: (
            <QuestionMark
              messageId="awsRoleExternalIdTooltip"
              messageValues={externalIdTooltipMessageValues}
              dataTestId="qmark_assume_role_external_id"
            />
          ),
        }}
        label={<FormattedMessage id="awsRoleExternalId" />}
        autoComplete="off"
        margin="none"
        minLength={EXTERNAL_ID_MIN_LENGTH}
        maxLength={EXTERNAL_ID_MAX_LENGTH}
        pattern={{
          value: EXTERNAL_ID_PATTERN,
          message: intl.formatMessage({ id: "invalidAwsExternalId" }),
        }}
        suppressErrorMessage
      />
    </FieldWithActionButton>
  );
};

const AwsAssumedRoleCredentials = ({
  readOnlyFields = [],
  hiddenFields = [],
  showExternalIdToggle = false,
}: {
  readOnlyFields?: string[];
  hiddenFields?: string[];
  showExternalIdToggle?: boolean;
}) => {
  const { watch } = useFormContext();

  const isReadOnly = (fieldName: string) => readOnlyFields.includes(fieldName);
  const isHidden = (fieldName: string) => hiddenFields.includes(fieldName);
  const isExternalIdReadOnly = isReadOnly(FIELD_NAMES.ASSUME_ROLE_EXTERNAL_ID);
  const isExternalIdHidden = isHidden(FIELD_NAMES.ASSUME_ROLE_EXTERNAL_ID);

  const useExternalId = watch(FIELD_NAMES.USE_EXTERNAL_ID);

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
      {showExternalIdToggle && <Switch name={FIELD_NAMES.USE_EXTERNAL_ID} label={<FormattedMessage id="awsUseExternalId" />} />}
      {!isExternalIdHidden && (!showExternalIdToggle || useExternalId) && (
        <ExternalIdTextInput readOnly={isExternalIdReadOnly} />
      )}
    </>
  );
};

export default AwsAssumedRoleCredentials;

import { FormControl } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { DropzoneArea } from "components/Dropzone";
import { TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAMES = Object.freeze({
  BILLING_DATA_DATASET: "billingDataDatasetName",
  BILLING_DATA_TABLE: "billingDataTableName",
  PROJECT_ID: "projectId",
  CREDENTIALS: "credentials"
});

const GcpCredentials = ({ hidden = [] }) => {
  const isHidden = (fieldName) => hidden.includes(fieldName);

  return (
    <>
      <FormControl fullWidth>
        <DropzoneArea acceptedFiles={["application/json"]} maxFileSizeMb={1} name={FIELD_NAMES.CREDENTIALS} />
      </FormControl>
      {!isHidden(FIELD_NAMES.BILLING_DATA_DATASET) && (
        <TextInput
          required
          dataTestId="input_billing_data_dataset_name"
          name={FIELD_NAMES.BILLING_DATA_DATASET}
          InputProps={{
            endAdornment: (
              <QuestionMark
                messageId="billingDataDatasetNameTooltip"
                messageValues={{
                  i: (chunks) => <i>{chunks}</i>
                }}
                dataTestId="qmark_billing_data_dataset_name"
              />
            )
          }}
          label={<FormattedMessage id="billingDataDatasetName" />}
          autoComplete="off"
        />
      )}
      {!isHidden(FIELD_NAMES.BILLING_DATA_DATASET) && (
        <TextInput
          required
          dataTestId="input_billing_data_table_name"
          name={FIELD_NAMES.BILLING_DATA_TABLE}
          InputProps={{
            endAdornment: <QuestionMark messageId="billingDataTableNameTooltip" dataTestId="qmark_billing_data_table_name" />
          }}
          label={<FormattedMessage id="billingDataTableName" />}
          autoComplete="off"
        />
      )}
      {!isHidden(FIELD_NAMES.PROJECT_ID) && (
        <TextInput
          name={FIELD_NAMES.PROJECT_ID}
          dataTestId="input_billing_data_project_id"
          InputProps={{
            endAdornment: <QuestionMark messageId="billingDataProjectIdTooltip" dataTestId="qmark_billing_data_project_id" />
          }}
          label={<FormattedMessage id="billingDataProjectId" />}
          autoComplete="off"
        />
      )}
    </>
  );
};

export default GcpCredentials;

import React from "react";
import { FormControl } from "@mui/material";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { DropzoneArea } from "components/Dropzone";
import Input from "components/Input";
import QuestionMark from "components/QuestionMark";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";

export const FIELD_NAMES = Object.freeze({
  BILLING_DATA_DATASET: "billingDataDatasetName",
  BILLING_DATA_TABLE: "billingDataTableName",
  CREDENTIALS: "credentials"
});

const GcpCredentials = ({ hidden = [] }) => {
  const { register, formState } = useFormContext();
  const { errors } = formState;
  const intl = useIntl();

  const isHidden = (fieldName) => hidden.includes(fieldName);

  return (
    <>
      <FormControl fullWidth>
        <DropzoneArea acceptedFiles={["application/json"]} maxFileSizeMb={1} name={FIELD_NAMES.CREDENTIALS} />
      </FormControl>
      {!isHidden(FIELD_NAMES.BILLING_DATA_DATASET) && (
        <Input
          required
          dataTestId="input_billing_data_dataset_name"
          name={FIELD_NAMES.BILLING_DATA_DATASET}
          error={!!errors[FIELD_NAMES.BILLING_DATA_DATASET]}
          helperText={errors[FIELD_NAMES.BILLING_DATA_DATASET] && errors[FIELD_NAMES.BILLING_DATA_DATASET].message}
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
          {...register(FIELD_NAMES.BILLING_DATA_DATASET, {
            required: {
              value: true,
              message: intl.formatMessage({ id: "thisFieldIsRequired" })
            },
            maxLength: {
              value: DEFAULT_MAX_INPUT_LENGTH,
              message: intl.formatMessage(
                { id: "maxLength" },
                { inputName: intl.formatMessage({ id: "billingDataDatasetName" }), max: DEFAULT_MAX_INPUT_LENGTH }
              )
            }
          })}
        />
      )}
      {!isHidden(FIELD_NAMES.BILLING_DATA_DATASET) && (
        <Input
          required
          dataTestId="input_billing_data_table_name"
          name={FIELD_NAMES.BILLING_DATA_TABLE}
          error={!!errors[FIELD_NAMES.BILLING_DATA_TABLE]}
          helperText={errors[FIELD_NAMES.BILLING_DATA_TABLE] && errors[FIELD_NAMES.BILLING_DATA_TABLE].message}
          InputProps={{
            endAdornment: <QuestionMark messageId="billingDataTableNameTooltip" dataTestId="qmark_billing_data_table_name" />
          }}
          label={<FormattedMessage id="billingDataTableName" />}
          autoComplete="off"
          {...register(FIELD_NAMES.BILLING_DATA_TABLE, {
            required: {
              value: true,
              message: intl.formatMessage({ id: "thisFieldIsRequired" })
            },
            maxLength: {
              value: DEFAULT_MAX_INPUT_LENGTH,
              message: intl.formatMessage(
                { id: "maxLength" },
                { inputName: intl.formatMessage({ id: "billingDataTableName" }), max: DEFAULT_MAX_INPUT_LENGTH }
              )
            }
          })}
        />
      )}
    </>
  );
};

export default GcpCredentials;

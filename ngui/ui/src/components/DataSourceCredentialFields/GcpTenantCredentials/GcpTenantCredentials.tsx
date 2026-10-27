import { FormControl } from "@mui/material";
import { useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { DropzoneArea } from "components/Dropzone";
import { Switch, TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";
import { ObjectValues } from "utils/types";

export const FIELD_NAMES = Object.freeze({
  CREDENTIALS: "credentials",
  BILLING_DATA_DATASET: "billingDataDatasetName",
  BILLING_DATA_TABLE: "billingDataTableName",
  AUTOMATICALLY_DETECT_PRICING_DATA: "automaticallyDetectPricingData",
  PRICING_DATA_DATASET: "pricingDataDatasetName",
  PRICING_DATA_TABLE: "pricingDataTableName",
});

type FieldName = ObjectValues<typeof FIELD_NAMES>;

type GcpTenantCredentialsProps = {
  hidden?: FieldName[];
};

const GcpTenantCredentials = ({ hidden = [] }: GcpTenantCredentialsProps) => {
  const isHidden = (fieldName: FieldName) => hidden.includes(fieldName);

  const anyPricingDataFieldVisible = [FIELD_NAMES.PRICING_DATA_DATASET, FIELD_NAMES.PRICING_DATA_TABLE].some(
    (fieldName) => !isHidden(fieldName)
  );

  const { watch } = useFormContext();

  const automaticallyDetectPricingData = watch(FIELD_NAMES.AUTOMATICALLY_DETECT_PRICING_DATA) ?? true;

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
                  i: (chunks) => <i>{chunks}</i>,
                }}
                dataTestId="qmark_billing_data_dataset_name"
              />
            ),
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
            endAdornment: <QuestionMark messageId="billingDataTableNameTooltip" dataTestId="qmark_billing_data_table_name" />,
          }}
          label={<FormattedMessage id="billingDataTableName" />}
          autoComplete="off"
        />
      )}
      {anyPricingDataFieldVisible && (
        <Switch
          name={FIELD_NAMES.AUTOMATICALLY_DETECT_PRICING_DATA}
          label={<FormattedMessage id="automaticallyDetectPricingData" />}
          // eslint-disable-next-line react/jsx-boolean-value
          defaultValue={true}
          adornment={
            <QuestionMark
              messageId="automaticallyDetectPricingDataDescription"
              dataTestId="qmark_automatically_detect_pricing_data"
            />
          }
        />
      )}
      {automaticallyDetectPricingData ? null : (
        <>
          {!isHidden(FIELD_NAMES.PRICING_DATA_DATASET) && (
            <TextInput
              required
              dataTestId="input_pricing_data_dataset_name"
              name={FIELD_NAMES.PRICING_DATA_DATASET}
              InputProps={{
                endAdornment: (
                  <QuestionMark
                    messageId="pricingDataDatasetNameTooltip"
                    messageValues={{
                      i: (chunks) => <i>{chunks}</i>,
                    }}
                    dataTestId="qmark_pricing_data_dataset_name"
                  />
                ),
              }}
              label={<FormattedMessage id="pricingDataDatasetName" />}
              autoComplete="off"
            />
          )}
          {!isHidden(FIELD_NAMES.PRICING_DATA_TABLE) && (
            <TextInput
              required
              dataTestId="input_pricing_data_table_name"
              name={FIELD_NAMES.PRICING_DATA_TABLE}
              InputProps={{
                endAdornment: (
                  <QuestionMark messageId="pricingDataTableNameTooltip" dataTestId="qmark_pricing_data_table_name" />
                ),
              }}
              label={<FormattedMessage id="pricingDataTableName" />}
              autoComplete="off"
            />
          )}
        </>
      )}
    </>
  );
};

export default GcpTenantCredentials;

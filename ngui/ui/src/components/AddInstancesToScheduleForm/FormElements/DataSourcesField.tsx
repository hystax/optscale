import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import DataSourceMultiSelect from "components/DataSourceMultiSelect";
import { useApiData } from "hooks/useApiData";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { ALIBABA_CNR, AWS_CNR, AZURE_CNR, GCP_CNR, NEBIUS } from "utils/constants";
import { FIELD_NAME as INSTANCES_FIELD_NAME } from "./InstancesField";

export const FIELD_NAME = "dataSources";

const SUPPORTED_DATA_SOURCE_TYPES = [AWS_CNR, AZURE_CNR, GCP_CNR, ALIBABA_CNR, NEBIUS];

const useDataSources = () => {
  const {
    apiData: { cloudAccounts: dataSources = [] }
  } = useApiData(GET_DATA_SOURCES);

  return dataSources.filter(({ type }) => SUPPORTED_DATA_SOURCE_TYPES.includes(type));
};

const DataSourcesField = () => {
  const intl = useIntl();
  const dataSources = useDataSources();

  const {
    control,
    formState: { errors },
    resetField
  } = useFormContext();

  return (
    <Controller
      name={FIELD_NAME}
      control={control}
      rules={{
        validate: {
          required: (value) => (isEmptyArray(value) ? intl.formatMessage({ id: "thisFieldIsRequired" }) : true)
        }
      }}
      render={({ field: { name, onBlur, onChange, ref, value } }) => (
        <DataSourceMultiSelect
          inputRef={ref}
          dataSourceIds={value}
          allDataSources={dataSources}
          onChange={(newValue) => {
            resetField(INSTANCES_FIELD_NAME);
            onChange(newValue);
          }}
          required
          fullWidth
          name={name}
          onBlur={onBlur}
          error={!!errors[FIELD_NAME]}
          helperText={errors?.[FIELD_NAME]?.message}
        />
      )}
    />
  );
};

export default DataSourcesField;

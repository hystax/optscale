import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import DataSourceMultiSelect from "components/DataSourceMultiSelect";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { FIELD_NAMES } from "../constants";
import { FormValues } from "../types";

const FIELD_NAME = FIELD_NAMES.DATA_SOURCES;

const DataSourcesField = ({ dataSources }) => {
  const intl = useIntl();

  const {
    control,
    formState: { errors },
    resetField
  } = useFormContext<FormValues>();

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
            // Reset selected buckets when selecting a new data source
            resetField(FIELD_NAMES.BUCKETS);
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

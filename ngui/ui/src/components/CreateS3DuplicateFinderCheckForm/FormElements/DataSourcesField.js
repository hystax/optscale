import React from "react";
import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import DataSourceMultiSelect from "components/DataSourceMultiSelect";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { FIELD_NAME as BUCKETS_FIELD_NAME } from "./BucketsField";

export const FIELD_NAME = "dataSources";

const DataSourcesField = ({ dataSources }) => {
  const intl = useIntl();

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
            // Reset selected buckets when selecting a new data source
            resetField(BUCKETS_FIELD_NAME);
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

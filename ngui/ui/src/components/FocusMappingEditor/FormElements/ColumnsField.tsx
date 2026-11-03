import { Autocomplete, Chip, TextField } from "@mui/material";
import { Controller, FieldError, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { idx } from "utils/objects";
import { hasColumnName } from "../validation";

type ColumnsFieldProps = {
  name: string;
};

const normalizeColumns = (columns: string[]) => [...new Set(columns.map((column) => column.trim()).filter(Boolean))];

// Column names are not known to the UI, so they are entered as free text: Enter (or leaving the input) adds a column
const ColumnsField = ({ name }: ColumnsFieldProps) => {
  const intl = useIntl();

  const {
    control,
    formState: { errors },
  } = useFormContext();

  const fieldError = idx(name.split("."), errors) as FieldError | undefined;

  return (
    <Controller
      name={name}
      control={control}
      rules={{
        validate: {
          columns: (columns: string[] | undefined) =>
            hasColumnName(columns) || intl.formatMessage({ id: "focusMappingColumnsRequired" }),
        },
      }}
      render={({ field: { value, onChange, onBlur, ref } }) => (
        <Autocomplete<string, true, true, true>
          freeSolo
          multiple
          autoSelect
          disableClearable
          options={[]}
          value={value ?? []}
          onChange={(event, newValue) => onChange(normalizeColumns(newValue))}
          onBlur={onBlur}
          renderTags={(columns, getTagProps) =>
            columns.map((column, index) => {
              const { key, ...tagProps } = getTagProps({ index });
              return <Chip key={key} size="small" variant="outlined" color="info" label={column} {...tagProps} />;
            })
          }
          renderInput={(params) => (
            <TextField
              {...params}
              inputRef={ref}
              required
              label={<FormattedMessage id="columns" />}
              inputProps={{ ...params.inputProps, "data-test-id": `input_${name}` }}
              error={!!fieldError}
              helperText={fieldError ? fieldError.message : <FormattedMessage id="focusMappingColumnsHelperText" />}
            />
          )}
        />
      )}
    />
  );
};

export default ColumnsField;

import { Autocomplete, TextField } from "@mui/material";
import { Controller, FieldError, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";
import { idx } from "utils/objects";
import { RESOURCE_TYPE_SUGGESTIONS } from "../constants";

type ResourceTypeFieldProps = {
  // Path of the type of a rule, e.g. "focusMapping.resourceType.rules.0.type"
  name: string;
};

// The type a rule sets: one of the standard OptScale resource types or any other text
const ResourceTypeField = ({ name }: ResourceTypeFieldProps) => {
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
          required: (value: string | undefined) =>
            (value ?? "").trim() !== "" || intl.formatMessage({ id: "thisFieldIsRequired" }),
          maxLength: (value: string | undefined) =>
            (value ?? "").length <= DEFAULT_MAX_INPUT_LENGTH ||
            intl.formatMessage({ id: "maxFieldLength" }, { max: DEFAULT_MAX_INPUT_LENGTH }),
        },
      }}
      render={({ field: { value, onChange, onBlur, ref } }) => (
        <Autocomplete<string, false, false, true>
          freeSolo
          options={RESOURCE_TYPE_SUGGESTIONS}
          value={value ?? ""}
          onChange={(event, newValue) => onChange(newValue ?? "")}
          onInputChange={(event, newInputValue) => onChange(newInputValue)}
          onBlur={onBlur}
          renderInput={(params) => (
            <TextField
              {...params}
              inputRef={ref}
              required
              label={<FormattedMessage id="type" />}
              inputProps={{ ...params.inputProps, "data-test-id": `input_${name}` }}
              error={!!fieldError}
              helperText={fieldError?.message}
            />
          )}
        />
      )}
    />
  );
};

export default ResourceTypeField;

import { Autocomplete } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.NAME;

type NameAutocompleteFieldProps = {
  perspectiveNames: string[];
};

const NameAutocompleteField = ({ perspectiveNames = [] }: NameAutocompleteFieldProps) => {
  const intl = useIntl();

  const {
    control,
    formState: { errors }
  } = useFormContext();

  return (
    <Controller
      name={FIELD_NAME}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      }}
      render={({ field: { value: formFieldValue, onChange } }) => (
        <Autocomplete
          freeSolo
          options={perspectiveNames}
          value={formFieldValue}
          onChange={(event, newValue) => {
            onChange(newValue);
          }}
          renderInput={(params) => (
            <Input
              {...params}
              inputProps={{
                ...params.inputProps,
                onChange: (e) => {
                  onChange(e.target.value);
                  params.inputProps?.onChange?.(e);
                }
              }}
              required
              dataTestId="input_save_as"
              label={<FormattedMessage id="saveAs" />}
              error={!!errors[FIELD_NAME]}
              helperText={errors[FIELD_NAME]?.message}
            />
          )}
        />
      )}
    />
  );
};

export default NameAutocompleteField;

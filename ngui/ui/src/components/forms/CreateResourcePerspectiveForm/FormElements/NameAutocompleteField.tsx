import { Autocomplete } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import PerspectiveNameLabel from "components/PerspectiveNameLabel";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.NAME;

type NameAutocompleteFieldProps = {
  perspectiveNames: string[];
};

const NAME_MAX_SIZE = 300;

const NameAutocompleteField = ({ perspectiveNames = [] }: NameAutocompleteFieldProps) => {
  const intl = useIntl();

  const {
    control,
    formState: { errors },
  } = useFormContext();

  return (
    <Controller
      name={FIELD_NAME}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" }),
        },
        maxLength: {
          value: NAME_MAX_SIZE,
          message: intl.formatMessage(
            { id: "maxLength" },
            { inputName: intl.formatMessage({ id: "name" }), max: NAME_MAX_SIZE }
          ),
        },
      }}
      render={({ field: { value: formFieldValue, onChange } }) => (
        <Autocomplete
          freeSolo
          options={perspectiveNames}
          value={formFieldValue}
          onChange={(event, newValue) => {
            onChange(newValue);
          }}
          renderOption={(props, option) => (
            <li {...props} key={option}>
              <PerspectiveNameLabel name={option} />
            </li>
          )}
          renderInput={(params) => (
            <Input
              {...params}
              inputProps={{
                ...params.inputProps,
                onChange: (e) => {
                  onChange(e.target.value);
                  params.inputProps?.onChange?.(e);
                },
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

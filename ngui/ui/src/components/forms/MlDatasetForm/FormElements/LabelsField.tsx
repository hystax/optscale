import { Autocomplete } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Chip from "components/Chip";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { FIELD_NAMES } from "../constants";
import { FormValues } from "../types";

const FIELD_NAME = FIELD_NAMES.LABELS;

const LabelsField = ({ labels = [], isLoading = false }) => {
  const {
    control,
    formState: { errors }
  } = useFormContext<FormValues>();

  return (
    <Controller
      name={FIELD_NAME}
      control={control}
      render={({ field: { value: formFieldValue, onChange } }) =>
        isLoading ? (
          <InputLoader fullWidth />
        ) : (
          <Autocomplete
            freeSolo
            value={formFieldValue}
            multiple
            onChange={(event, newValue) => {
              onChange(newValue);
            }}
            disableClearable
            clearOnBlur
            options={labels.map((label) => label)}
            renderTags={(autocompleteValue, getTagProps) =>
              autocompleteValue.map((option, index) => (
                <Chip key={option} variant="outlined" color="info" label={option} {...getTagProps({ index })} />
              ))
            }
            renderInput={(params) => (
              <Input
                {...params}
                dataTestId="input_labels"
                label={<FormattedMessage id="labels" />}
                error={!!errors[FIELD_NAME]}
                helperText={errors[FIELD_NAME]?.message}
              />
            )}
          />
        )
      }
    />
  );
};

export default LabelsField;

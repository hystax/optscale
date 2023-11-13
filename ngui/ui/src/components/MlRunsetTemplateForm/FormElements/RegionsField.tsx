import { Autocomplete } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Chip from "components/Chip";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { RUNSET_TEMPLATE_REGIONS } from "utils/constants";

export const FIELD_NAME = "regions";

const RegionsField = ({ isLoading }) => {
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
        validate: {
          required: (value) => (!isEmptyArray(value) ? true : intl.formatMessage({ id: "thisFieldIsRequired" }))
        }
      }}
      render={({ field: { value: formFieldValue, onChange } }) =>
        isLoading ? (
          <InputLoader fullWidth />
        ) : (
          <Autocomplete
            value={formFieldValue}
            multiple
            disableClearable
            clearOnBlur
            onChange={(event, newValue) => {
              onChange(newValue);
            }}
            options={RUNSET_TEMPLATE_REGIONS}
            isOptionEqualToValue={(option, value) => option.name === value.name}
            getOptionLabel={(option) => option.name}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip key={option.name} variant="outlined" color="info" label={option.name} {...getTagProps({ index })} />
              ))
            }
            renderInput={(params) => (
              <Input
                {...params}
                dataTestId="input_data_sources"
                label={<FormattedMessage id="regions" />}
                required
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

export default RegionsField;

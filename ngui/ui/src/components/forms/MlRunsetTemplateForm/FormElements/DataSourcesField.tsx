import { Autocomplete } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Chip from "components/Chip";
import CloudLabel from "components/CloudLabel";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { AWS_CNR } from "utils/constants";
import { FIELD_NAMES } from "../constants";

export const FIELD_NAME = FIELD_NAMES.DATA_SOURCES;

const DataSourcesField = ({ dataSources, isLoading }) => {
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
            options={dataSources
              .filter(({ type }) => type === AWS_CNR)
              .map(({ id, name, type }) => ({
                id,
                name,
                type
              }))}
            isOptionEqualToValue={(option, value) => option.id === value.id}
            getOptionLabel={(option) => <CloudLabel name={option.name} type={option.type} disableLink />}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip
                  key={option.name}
                  variant="outlined"
                  color="info"
                  label={<CloudLabel name={option.name} type={option.type} disableLink />}
                  {...getTagProps({ index })}
                />
              ))
            }
            renderInput={(params) => (
              <Input
                {...params}
                dataTestId="input_data_sources"
                label={<FormattedMessage id="dataSources" />}
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

export default DataSourcesField;

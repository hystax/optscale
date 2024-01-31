import { Autocomplete } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Chip from "components/Chip";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import QuestionMark from "components/QuestionMark";
import { FIELD_NAMES } from "../constants";

export const FIELD_NAME = FIELD_NAMES.PRIMARY_METRIC_FIELD_NAME;

const PrimaryMetricSelector = ({ metrics = [], isLoading = false }) => {
  const {
    control,
    formState: { errors },
    setValue,
    getValues
  } = useFormContext();

  const intl = useIntl();

  return (
    <Controller
      name={FIELD_NAME}
      control={control}
      rules={{
        validate: {
          required: (value) => (value ? true : intl.formatMessage({ id: "thisFieldIsRequired" }))
        }
      }}
      render={({ field: { name, value: formFieldValue, onBlur, onChange, ref } }) =>
        isLoading ? (
          <InputLoader fullWidth />
        ) : (
          <Autocomplete
            name={name}
            value={formFieldValue}
            onChange={(event, newValue) => {
              onChange(newValue);

              const secondaryMetrics = getValues(FIELD_NAMES.SECONDARY_METRICS_FIELD_NAME);
              setValue(
                FIELD_NAMES.SECONDARY_METRICS_FIELD_NAME,
                secondaryMetrics.filter((secondaryMetric) => secondaryMetric.id !== newValue.id)
              );
            }}
            onBlur={onBlur}
            disableClearable
            clearOnBlur
            isOptionEqualToValue={(option, value) => option.id === value.id}
            options={metrics.map((metric) => ({
              name: metric.name,
              id: metric.id
            }))}
            getOptionLabel={(option) => option?.name ?? ""}
            renderTags={(autocompleteValue, getTagProps) =>
              autocompleteValue.map((option, index) => (
                <Chip key={option.name} variant="outlined" color="info" label={option.name} {...getTagProps({ index })} />
              ))
            }
            renderInput={(params) => (
              <Input
                {...params}
                dataTestId="input_primary_metrics"
                label={<FormattedMessage id="primaryMetric" />}
                error={!!errors[FIELD_NAME]}
                helperText={errors[FIELD_NAME]?.message}
                InputProps={{
                  ...params.InputProps,
                  endAdornment: (
                    <>
                      <QuestionMark messageId="primaryMetricHint" dataTestId="qmark_primary_metric" />
                      {params.InputProps.endAdornment}
                    </>
                  )
                }}
                required
                ref={ref}
              />
            )}
          />
        )
      }
    />
  );
};

export default PrimaryMetricSelector;

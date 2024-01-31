import { Autocomplete } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Chip from "components/Chip";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import QuestionMark from "components/QuestionMark";
import { FIELD_NAMES } from "../constants";

export const FIELD_NAME = FIELD_NAMES.SECONDARY_METRICS_FIELD_NAME;

const SecondaryMetricsSelector = ({ metrics = [], isLoading = false }) => {
  const {
    control,
    formState: { errors },
    watch
  } = useFormContext();

  const primaryMetric = watch(FIELD_NAMES.PRIMARY_METRIC_FIELD_NAME);

  return (
    <Controller
      name={FIELD_NAME}
      control={control}
      render={({ field: { value: formFieldValue, onChange } }) =>
        isLoading ? (
          <InputLoader fullWidth />
        ) : (
          <Autocomplete
            value={formFieldValue}
            multiple
            onChange={(event, newValue) => {
              onChange(newValue);
            }}
            disableClearable
            clearOnBlur
            isOptionEqualToValue={(option, value) => option.id === value.id}
            options={(primaryMetric ? metrics.filter((metric) => metric.id !== primaryMetric.id) : metrics).map((metric) => ({
              name: metric.name,
              id: metric.id
            }))}
            getOptionLabel={(option) => option.name}
            renderTags={(autocompleteValue, getTagProps) =>
              autocompleteValue.map((option, index) => (
                <Chip key={option.name} variant="outlined" color="info" label={option.name} {...getTagProps({ index })} />
              ))
            }
            renderInput={(params) => (
              <Input
                {...params}
                dataTestId="input_secondary_metrics"
                label={<FormattedMessage id="secondaryMetrics" />}
                error={!!errors[FIELD_NAME]}
                helperText={errors[FIELD_NAME]?.message}
                InputProps={{
                  ...params.InputProps,
                  endAdornment: (
                    <>
                      <QuestionMark messageId="secondaryMetricsHint" dataTestId="qmark_secondary_metrics" />
                      {params.InputProps.endAdornment}
                    </>
                  )
                }}
              />
            )}
          />
        )
      }
    />
  );
};

export default SecondaryMetricsSelector;

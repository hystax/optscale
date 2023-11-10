import { useEffect } from "react";
import { FormControl, FormControlLabel } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Checkbox from "components/Checkbox";
import Input from "components/Input";
import QuestionMark from "components/QuestionMark";
import { positiveInteger } from "utils/validation";

export const USE_SPOT_INSTANCES_CHECKBOX_FIELD_NAME = "useSpotInstances";
export const MAX_ATTEMPTS_FIELD_NAME = "maxAttempts";

const SpotInstanceFields = () => {
  const intl = useIntl();

  const { control, formState, watch, register, trigger } = useFormContext();

  const { errors, isSubmitted } = formState;

  const isEnabled = watch(USE_SPOT_INSTANCES_CHECKBOX_FIELD_NAME);

  useEffect(() => {
    /**
     * The checkbox and max attempts are linked - the max attempts should only be validated if the checkbox is checked.
     * We need to manually trigger budget field validation when the checkbox state is changed,
     * if it was changed after the form was submitted but validation errors occurred.
     * During form validation, fields are only validated when their values are changed,
     * so we need to trigger the budget validation when the checkbox is changed
     */
    if (isSubmitted) {
      trigger(MAX_ATTEMPTS_FIELD_NAME);
    }
  }, [isSubmitted, trigger, isEnabled]);

  return (
    <FormControl fullWidth>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "flex-start" }}>
        <FormControlLabel
          control={
            <Controller
              name={USE_SPOT_INSTANCES_CHECKBOX_FIELD_NAME}
              control={control}
              render={({ field: { value, onChange, ...rest } }) => (
                <Checkbox
                  data-test-id="checkbox_use_spot_instances"
                  checked={value}
                  onChange={(event) => {
                    onChange(event.target.checked);
                  }}
                  {...rest}
                />
              )}
            />
          }
          label={<FormattedMessage id="requestSpotInstances" />}
        />
        <div
          style={{
            flexGrow: 1
          }}
        >
          <Input
            margin="none"
            label={<FormattedMessage id="maxAttempts" />}
            dataTestId="input_max_tries"
            error={!!errors[MAX_ATTEMPTS_FIELD_NAME]}
            helperText={errors[MAX_ATTEMPTS_FIELD_NAME] && errors[MAX_ATTEMPTS_FIELD_NAME].message}
            {...register(MAX_ATTEMPTS_FIELD_NAME, {
              required: isEnabled
                ? {
                    value: true,
                    message: intl.formatMessage({ id: "thisFieldIsRequired" })
                  }
                : undefined,
              max: isEnabled
                ? {
                    value: 64,
                    message: intl.formatMessage({ id: "lessOrEqual" }, { max: 64 })
                  }
                : undefined,
              min: isEnabled
                ? {
                    value: 1,
                    message: intl.formatMessage({ id: "moreOrEqual" }, { min: 1 })
                  }
                : undefined,
              validate: isEnabled
                ? {
                    positiveInteger: (value) => positiveInteger(value)
                  }
                : undefined
            })}
            InputProps={{
              endAdornment: (
                <QuestionMark
                  messageId="maxAttemptsTooltip"
                  messageValues={{
                    i: (chunks) => <i>{chunks}</i>
                  }}
                  dataTestId="qmark_max_attempts"
                />
              )
            }}
          />
        </div>
      </div>
    </FormControl>
  );
};

export default SpotInstanceFields;

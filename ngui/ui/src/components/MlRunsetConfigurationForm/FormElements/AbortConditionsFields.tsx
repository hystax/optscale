import { useEffect } from "react";
import { FormControlLabel, InputAdornment, Stack } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Checkbox from "components/Checkbox";
import Input from "components/Input";
import Tooltip from "components/Tooltip";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { MAX_INT_32 } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { positiveInteger } from "utils/validation";

export const MAX_BUDGET_CHECKBOX_FIELD_NAME = "maxBudgetCheckbox";
export const MAX_BUDGET_VALUE_FIELD_NAME = "maxBudgetValue";

export const REACHED_GOALS_CHECKBOX_FIELD_NAME = "reachedGoalsCheckbox";

export const MAX_DURATION_CHECKBOX_FIELD_NAME = "maxDurationCheckbox";
export const MAX_DURATION_VALUE_FIELD_NAME = "maxDurationValue";

const inputWidthStyle = {
  flexGrow: 1
};

const blockStyle = { display: "flex", flexWrap: "wrap", alignItems: "flex-start" };

const MaxBudget = () => {
  const intl = useIntl();

  const { control, formState, watch, register, trigger } = useFormContext();

  const { errors, isSubmitted } = formState;

  const { currencySymbol } = useOrganizationInfo();

  const isEnabled = watch(MAX_BUDGET_CHECKBOX_FIELD_NAME);

  useEffect(() => {
    /**
     * The checkbox and budget are linked - the budget should only be validated if the checkbox is checked.
     * We need to manually trigger budget field validation when the checkbox state is changed,
     * if it was changed after the form was submitted but validation errors occurred.
     * During form validation, fields are only validated when their values are changed,
     * so we need to trigger the budget validation when the checkbox is changed
     */
    if (isSubmitted) {
      trigger(MAX_BUDGET_VALUE_FIELD_NAME);
    }
  }, [isSubmitted, trigger, isEnabled]);

  return (
    <div style={blockStyle}>
      <FormControlLabel
        control={
          <Controller
            name={MAX_BUDGET_CHECKBOX_FIELD_NAME}
            control={control}
            render={({ field: { value, onChange, ...rest } }) => (
              <Checkbox
                data-test-id="checkbox_max_budget"
                checked={value}
                onChange={(event) => {
                  onChange(event.target.checked);
                }}
                {...rest}
              />
            )}
          />
        }
        label={<FormattedMessage id="abortRunsetWhenProjectedExpensesExceed" />}
      />
      <div style={inputWidthStyle}>
        <Input
          margin="none"
          dataTestId="input_maximum_runset_budget"
          required
          error={!!errors[MAX_BUDGET_VALUE_FIELD_NAME]}
          helperText={errors[MAX_BUDGET_VALUE_FIELD_NAME] && errors[MAX_BUDGET_VALUE_FIELD_NAME].message}
          {...register(MAX_BUDGET_VALUE_FIELD_NAME, {
            required: isEnabled
              ? {
                  value: true,
                  message: intl.formatMessage({ id: "thisFieldIsRequired" })
                }
              : undefined,
            max: isEnabled
              ? {
                  value: MAX_INT_32,
                  message: intl.formatMessage({ id: "lessOrEqual" }, { max: MAX_INT_32 })
                }
              : undefined,
            validate: isEnabled
              ? {
                  positiveInteger: (value) => positiveInteger(value)
                }
              : undefined
          })}
          InputProps={{
            endAdornment: <InputAdornment position="end">{currencySymbol}</InputAdornment>
          }}
        />
      </div>
    </div>
  );
};

const ReachedGoals = () => {
  const { control } = useFormContext();

  return (
    <div style={blockStyle}>
      <FormControlLabel
        control={
          <Controller
            name={REACHED_GOALS_CHECKBOX_FIELD_NAME}
            control={control}
            render={({ field: { value, onChange, ...rest } }) => (
              <Checkbox
                data-test-id="checkbox_reached_goals"
                checked={value}
                onChange={(event) => onChange(event.target.checked)}
                {...rest}
              />
            )}
          />
        }
        label={<FormattedMessage id="abortRunsetWhenOneOfRunsReachesTaskGoals" />}
      />
    </div>
  );
};

const MaxDuration = () => {
  const intl = useIntl();

  const {
    control,
    formState: { errors, isSubmitted },
    watch,
    register,
    trigger
  } = useFormContext();

  const isEnabled = watch(MAX_DURATION_CHECKBOX_FIELD_NAME);

  useEffect(() => {
    /**
     * The checkbox and duration are linked - the duration should only be validated if the checkbox is checked.
     * We need to manually trigger duration field validation when the checkbox state is changed,
     * if it was changed after the form was submitted but validation errors occurred.
     * During form validation, fields are only validated when their values are changed,
     * so we need to trigger the duration validation when the checkbox is changed
     */
    if (isSubmitted) {
      trigger(MAX_DURATION_VALUE_FIELD_NAME);
    }
  }, [isSubmitted, trigger, isEnabled]);

  return (
    <div style={blockStyle}>
      <FormControlLabel
        control={
          <Controller
            name={MAX_DURATION_CHECKBOX_FIELD_NAME}
            control={control}
            render={({ field: { value, onChange, ...rest } }) => (
              <Checkbox
                data-test-id="checkbox_max_duration"
                checked={value}
                onChange={(event) => onChange(event.target.checked)}
                {...rest}
              />
            )}
          />
        }
        label={<FormattedMessage id="abortIndividualRunIfItsDurationExceeds" />}
      />
      <div style={inputWidthStyle}>
        <Input
          margin="none"
          dataTestId="input_max_duration"
          required
          error={!!errors[MAX_DURATION_VALUE_FIELD_NAME]}
          helperText={errors[MAX_DURATION_VALUE_FIELD_NAME] && errors[MAX_DURATION_VALUE_FIELD_NAME].message}
          {...register(MAX_DURATION_VALUE_FIELD_NAME, {
            required: isEnabled
              ? {
                  value: true,
                  message: intl.formatMessage({ id: "thisFieldIsRequired" })
                }
              : undefined,
            max: isEnabled
              ? {
                  value: MAX_INT_32,
                  message: intl.formatMessage({ id: "lessOrEqual" }, { max: MAX_INT_32 })
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
              <InputAdornment position="end">{intl.formatMessage({ id: "min" }).toLocaleLowerCase()}</InputAdornment>
            )
          }}
        />
      </div>
    </div>
  );
};

const GoalsPlateau = () => (
  <div style={blockStyle}>
    <Tooltip title={<FormattedMessage id="comingSoon" />}>
      <FormControlLabel control={<Checkbox disabled />} label={<FormattedMessage id="abortIndividualRunIfTaskGoalPlateau" />} />
    </Tooltip>
  </div>
);

const AbortConditionsFields = () => (
  <Stack spacing={SPACING_1}>
    <MaxBudget />
    <MaxDuration />
    <ReachedGoals />
    <GoalsPlateau />
  </Stack>
);

export default AbortConditionsFields;

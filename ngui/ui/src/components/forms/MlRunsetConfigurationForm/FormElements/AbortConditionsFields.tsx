import { useEffect } from "react";
import { FormControlLabel, InputAdornment, Stack } from "@mui/material";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import CheckboxComponent from "components/Checkbox";
import { Checkbox as CheckboxField, NumberInput } from "components/forms/common/fields";
import Tooltip from "components/Tooltip";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { MAX_INT_32 } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { positiveInteger } from "utils/validation";
import { FIELD_NAMES } from "../constants";
import { FormValues } from "../types";

const MAX_BUDGET_CHECKBOX_FIELD_NAME = FIELD_NAMES.MAX_BUDGET_CHECKBOX;
const MAX_BUDGET_VALUE_FIELD_NAME = FIELD_NAMES.MAX_BUDGET_VALUE;

const REACHED_GOALS_CHECKBOX_FIELD_NAME = FIELD_NAMES.REACHED_GOALS_CHECKBOX;

const MAX_DURATION_CHECKBOX_FIELD_NAME = FIELD_NAMES.MAX_DURATION_CHECKBOX;
const MAX_DURATION_VALUE_FIELD_NAME = FIELD_NAMES.MAX_DURATION_VALUE;

const inputWidthStyle = {
  flexGrow: 1
};

const blockStyle = { display: "flex", flexWrap: "wrap", alignItems: "flex-start" };

const MaxBudget = () => {
  const { formState, watch, trigger } = useFormContext<FormValues>();

  const { isSubmitted } = formState;

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
      <CheckboxField
        name={MAX_BUDGET_CHECKBOX_FIELD_NAME}
        label={<FormattedMessage id="abortRunsetWhenProjectedExpensesExceed" />}
      />
      <div style={inputWidthStyle}>
        <NumberInput
          name={MAX_BUDGET_VALUE_FIELD_NAME}
          margin="none"
          dataTestId="input_maximum_runset_budget"
          required={isEnabled}
          max={isEnabled ? MAX_INT_32 : null}
          validate={isEnabled ? { positiveInteger: (value) => positiveInteger(value) } : undefined}
          InputProps={{
            endAdornment: <InputAdornment position="end">{currencySymbol}</InputAdornment>
          }}
        />
      </div>
    </div>
  );
};

const ReachedGoals = () => (
  <div style={blockStyle}>
    <CheckboxField
      name={REACHED_GOALS_CHECKBOX_FIELD_NAME}
      label={<FormattedMessage id="abortRunsetWhenOneOfRunsReachesTaskGoals" />}
    />
  </div>
);

const MaxDuration = () => {
  const intl = useIntl();

  const {
    formState: { isSubmitted },
    watch,
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
      <CheckboxField
        name={MAX_DURATION_CHECKBOX_FIELD_NAME}
        label={<FormattedMessage id="abortIndividualRunIfItsDurationExceeds" />}
      />
      <div style={inputWidthStyle}>
        <NumberInput
          name={MAX_DURATION_VALUE_FIELD_NAME}
          margin="none"
          dataTestId="input_max_duration"
          required={isEnabled}
          max={isEnabled ? MAX_INT_32 : null}
          validate={isEnabled ? { positiveInteger: (value) => positiveInteger(value) } : undefined}
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
      <FormControlLabel
        control={<CheckboxComponent disabled />}
        label={<FormattedMessage id="abortIndividualRunIfTaskGoalPlateau" />}
      />
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

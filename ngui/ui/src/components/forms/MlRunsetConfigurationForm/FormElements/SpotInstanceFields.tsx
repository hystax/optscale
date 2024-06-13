import { useEffect } from "react";
import { FormControl } from "@mui/material";
import { useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { Checkbox, NumberInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";
import { positiveInteger } from "utils/validation";
import { FIELD_NAMES } from "../constants";
import { FormValues } from "../types";

const USE_SPOT_INSTANCES_CHECKBOX_FIELD_NAME = FIELD_NAMES.USE_SPOT_INSTANCES;
const MAX_ATTEMPTS_FIELD_NAME = FIELD_NAMES.MAX_ATTEMPTS;

const SpotInstanceFields = () => {
  const { formState, watch, trigger } = useFormContext<FormValues>();

  const { isSubmitted } = formState;

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
        <Checkbox name={USE_SPOT_INSTANCES_CHECKBOX_FIELD_NAME} label={<FormattedMessage id="requestSpotInstances" />} />
        <div
          style={{
            flexGrow: 1
          }}
        >
          <NumberInput
            name={MAX_ATTEMPTS_FIELD_NAME}
            margin="none"
            label={<FormattedMessage id="maxAttempts" />}
            dataTestId="input_max_tries"
            required={isEnabled}
            max={isEnabled ? 64 : null}
            min={isEnabled ? 1 : null}
            validate={isEnabled ? { positiveInteger: (value) => positiveInteger(value) } : undefined}
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

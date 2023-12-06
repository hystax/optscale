import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import IntervalTimePicker from "components/IntervalTimePicker";
import { EN_FORMAT, getNYearsFromToday } from "utils/datetime";
import { FIELD_NAMES } from "../constants";

const InitiationDateField = ({ name = FIELD_NAMES.INITIATION_DATE }) => {
  const {
    control,
    trigger,
    formState: { errors, isSubmitted }
  } = useFormContext();

  const intl = useIntl();

  return (
    <Controller
      name={name}
      control={control}
      rules={{
        validate: {
          isLessThanExpirationDate: (value, formValues) => {
            const expirationDate = formValues[FIELD_NAMES.EXPIRATION_DATE];

            if (!expirationDate || !value) {
              return true;
            }

            return (
              value <= expirationDate ||
              intl.formatMessage(
                { id: "xShouldBeLessThanOrEqualToY" },
                {
                  x: intl.formatMessage({ id: "initiationDate" }),
                  y: intl.formatMessage({ id: "expirationDate" })
                }
              )
            );
          }
        }
      }}
      render={({ field: { name: fieldName, onChange, value } }) => (
        <IntervalTimePicker
          labelMessageId="initiationDate"
          value={value}
          onApply={(date) => {
            onChange(date);
            if (isSubmitted) {
              trigger(FIELD_NAMES.EXPIRATION_DATE);
            }
          }}
          fullWidth
          margin="dense"
          format={EN_FORMAT}
          maxDate={getNYearsFromToday(5)}
          notSetMessageId="initiationDate"
          validation={{
            dataTestId: `input_${fieldName}`,
            error: !!errors[fieldName],
            helperText: errors[fieldName]?.message
          }}
          dataTestIds={{
            field: {
              input: `input_${fieldName}`,
              iconButton: `btn_${fieldName}select_date`
            }
          }}
        />
      )}
    />
  );
};

export default InitiationDateField;

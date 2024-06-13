import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import InputLoader from "components/InputLoader";
import IntervalTimePicker from "components/IntervalTimePicker";
import { EN_FORMAT, getNYearsFromToday } from "utils/datetime";
import { FIELD_NAMES } from "../constants";

const ExpirationDateField = ({ name = FIELD_NAMES.EXPIRATION_DATE, isLoading = false }) => {
  const {
    control,
    trigger,
    formState: { errors, isSubmitted }
  } = useFormContext();

  const intl = useIntl();

  return isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <Controller
      name={name}
      control={control}
      rules={{
        validate: {
          isGreaterThanInitiationDate: (value, formValues) => {
            const initiationDate = formValues[FIELD_NAMES.INITIATION_DATE];
            if (!(initiationDate && value)) {
              return true;
            }
            return (
              value >= initiationDate ||
              intl.formatMessage(
                { id: "xMustBeGreaterThanOrEqualToY" },
                {
                  x: intl.formatMessage({ id: "expirationDate" }),
                  y: intl.formatMessage({ id: "initiationDate" })
                }
              )
            );
          }
        }
      }}
      render={({ field: { name: fieldName, onChange, value } }) => (
        <IntervalTimePicker
          labelMessageId="expirationDate"
          value={value}
          onApply={(date) => {
            onChange(date);
            if (isSubmitted) {
              trigger(FIELD_NAMES.INITIATION_DATE);
            }
          }}
          fullWidth
          margin="dense"
          format={EN_FORMAT}
          maxDate={getNYearsFromToday(5)}
          notSetMessageId="expirationDate"
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

export default ExpirationDateField;

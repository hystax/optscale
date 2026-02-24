import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import IntervalTimePicker from "components/IntervalTimePicker";
import { EN_FORMAT, startOfMonth, subDays, subYears } from "utils/datetime";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.IMPORT_FROM;

const ReimportFromDatePicker = () => {
  const intl = useIntl();

  const {
    control,
    formState: { errors },
  } = useFormContext();

  return (
    <Controller
      name={FIELD_NAME}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" }),
        },
      }}
      render={({ field: { value, onChange } }) => (
        <IntervalTimePicker
          labelMessageId="importFrom"
          value={value}
          required
          notSetMessageId="notSet"
          onApply={onChange}
          fullWidth
          format={EN_FORMAT}
          margin="dense"
          minDate={+subYears(new Date(), 1)}
          maxDate={+subDays(startOfMonth(new Date()), 1)}
          validation={{
            dataTestId: `input_${FIELD_NAME}`,
            error: !!errors[FIELD_NAME],
            helperText: errors[FIELD_NAME]?.message,
          }}
          dataTestIds={{
            field: {
              input: `input_${FIELD_NAME}`,
              iconButton: "btn_select_date",
            },
          }}
        />
      )}
    />
  );
};

export default ReimportFromDatePicker;

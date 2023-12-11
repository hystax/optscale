import { Box, FormControl, FormHelperText } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Day from "components/DateRangePicker/Day";
import Selector from "components/Selector";
import { MERIDIEM_NAMES } from "utils/datetime";
import { FIELD_NAMES, TIME_VALUES } from "../constants";

const PowerOffField = ({ name = FIELD_NAMES.POWER_OFF.FIELD }) => {
  const {
    formState: { errors },
    control
  } = useFormContext();

  const intl = useIntl();

  return (
    <Controller
      name={name}
      control={control}
      rules={{
        validate: {
          required: (value) => (!value.time ? intl.formatMessage({ id: "thisFieldIsRequired" }) : true)
        }
      }}
      render={({ field: { name: fieldName, onBlur, onChange, ref, value } }) => (
        <FormControl fullWidth>
          <Box display="flex" alignItems="center">
            <Selector
              margin="none"
              name={fieldName}
              fullWidth
              required
              value={value[FIELD_NAMES.POWER_OFF.TIME]}
              error={!!errors[fieldName]}
              onChange={(newTime) =>
                onChange({
                  ...value,
                  time: newTime
                })
              }
              data={{ items: TIME_VALUES.map((timeValue) => ({ name: timeValue, value: timeValue })) }}
              labelId="instancePowerOff"
              ref={ref}
              onBlur={onBlur}
              MenuProps={{
                sx: {
                  height: "300px"
                }
              }}
            />
            {Object.values(MERIDIEM_NAMES).map((daytimeName) => (
              <Day
                key={daytimeName}
                outlined={value[FIELD_NAMES.POWER_OFF.TIME_OF_DAY] === daytimeName}
                filled={value[FIELD_NAMES.POWER_OFF.TIME_OF_DAY] === daytimeName}
                onClick={() =>
                  onChange({
                    ...value,
                    timeOfDay: daytimeName
                  })
                }
                value={daytimeName}
              />
            ))}
          </Box>
          {!!errors[fieldName] && <FormHelperText error>{errors?.[fieldName]?.message}</FormHelperText>}
        </FormControl>
      )}
    />
  );
};

export default PowerOffField;

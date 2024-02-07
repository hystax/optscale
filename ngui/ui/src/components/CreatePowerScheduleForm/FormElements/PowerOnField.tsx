import { Box, FormControl, FormHelperText } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Day from "components/DateRangePicker/Day";
import Selector, { Item, ItemContent } from "components/Selector";
import { MERIDIEM_NAMES } from "utils/datetime";
import { FIELD_NAMES, TIME_VALUES } from "../constants";

const PowerOnField = ({ name = FIELD_NAMES.POWER_ON.FIELD }) => {
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
      render={({ field: { onChange, value, ...rest } }) => (
        <FormControl fullWidth>
          <Box display="flex" alignItems="center">
            <Selector
              id="power-on-selector"
              margin="none"
              fullWidth
              required
              value={value[FIELD_NAMES.POWER_ON.TIME]}
              error={!!errors[name]}
              onChange={(newTime) =>
                onChange({
                  ...value,
                  time: newTime
                })
              }
              labelMessageId="instancePowerOn"
              sx={{
                marginRight: (theme) => theme.spacing(1)
              }}
              {...rest}
            >
              {TIME_VALUES.map((timeValue) => (
                <Item key={timeValue} value={timeValue}>
                  <ItemContent>{timeValue}</ItemContent>
                </Item>
              ))}
            </Selector>
            {Object.values(MERIDIEM_NAMES).map((daytimeName) => (
              <Day
                key={daytimeName}
                outlined={value[FIELD_NAMES.POWER_ON.TIME_OF_DAY] === daytimeName}
                filled={value[FIELD_NAMES.POWER_ON.TIME_OF_DAY] === daytimeName}
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
          {!!errors[name] && <FormHelperText error>{errors?.[name]?.message}</FormHelperText>}
        </FormControl>
      )}
    />
  );
};

export default PowerOnField;

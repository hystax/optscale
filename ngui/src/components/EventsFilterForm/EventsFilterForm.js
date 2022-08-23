import React, { useState } from "react";
import Box from "@mui/material/Box";
import MenuItem from "@mui/material/MenuItem";
import TextField from "@mui/material/TextField";
import PropTypes from "prop-types";
import { useForm, Controller, FormProvider } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import RangePickerFormField from "components/RangePickerFormField";
import { EVENT_LEVEL } from "utils/constants";
import { getQueryParams } from "utils/network";

const LEVEL = "level";
const START_DATE_TIME = "startDateTime";
const END_DATE_TIME = "endDateTime";

const eventLevels = [
  {
    value: EVENT_LEVEL.ALL,
    label: <FormattedMessage id="all" />
  },
  {
    value: EVENT_LEVEL.INFO,
    label: <FormattedMessage id="info" />
  },
  {
    value: EVENT_LEVEL.SUCCESS,
    label: <FormattedMessage id="success" />
  },
  {
    value: EVENT_LEVEL.WARNING,
    label: <FormattedMessage id="warning" />
  },
  {
    value: EVENT_LEVEL.ERROR,
    label: <FormattedMessage id="error" />
  }
];

const EventsFilterForm = ({ onSubmit }) => {
  const filterParams = getQueryParams();

  const [defaultStartDate, setDefaultStartDate] = useState(filterParams.timeStart ? Number(filterParams.timeStart) : null);
  const [defaultEndDate, setDefaultEndDate] = useState(filterParams.timeEnd ? Number(filterParams.timeEnd) : null);

  const methods = useForm({
    defaultValues: {
      [LEVEL]: filterParams.level || EVENT_LEVEL.ALL,
      [START_DATE_TIME]: defaultStartDate,
      [END_DATE_TIME]: defaultEndDate
    }
  });

  const { handleSubmit, control } = methods;

  return (
    <FormProvider {...methods}>
      <form
        onSubmit={handleSubmit((data) => {
          const submitLevel = data[LEVEL] !== EVENT_LEVEL.ALL ? data[LEVEL] : undefined;
          onSubmit({
            level: submitLevel,
            timeStart: data[START_DATE_TIME],
            timeEnd: data[END_DATE_TIME]
          });
        })}
      >
        <Box mb={2} display="grid">
          <Controller
            name={LEVEL}
            control={control}
            render={({ field }) => (
              <TextField
                select
                variant="outlined"
                label={<FormattedMessage id="eventLevel" />}
                InputProps={{
                  "data-test-id": "select_ev_level"
                }}
                {...field}
              >
                {eventLevels.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            )}
          />
        </Box>
        {/* minmax thing to prevent picker overflow: https://css-tricks.com/preventing-a-grid-blowout/ */}
        <Box ml={0} mb={2} display="grid" style={{ gridTemplateColumns: "minmax(0, 1fr)" }}>
          <RangePickerFormField
            startDatePickerName={START_DATE_TIME}
            endDatePickerName={END_DATE_TIME}
            defaultStartDate={defaultStartDate}
            defaultEndDate={defaultEndDate}
            onStartDateChange={(dateTime) => setDefaultStartDate(dateTime)}
            onEndDateChange={(dateTime) => setDefaultEndDate(dateTime)}
            notSetMessageId="latest"
          />
        </Box>
        <Box display="flex" justifyContent="flex-end">
          <Button dataTestId="btn_apply" variant="contained" messageId="apply" color="primary" type="submit" />
        </Box>
      </form>
    </FormProvider>
  );
};

EventsFilterForm.propTypes = {
  onSubmit: PropTypes.func.isRequired
};

export default EventsFilterForm;

import React, { useState } from "react";
import { Select, MenuItem } from "@mui/material";
import { subHours, parse } from "date-fns";
import PropTypes from "prop-types";
import Day from "components/DateRangePicker/Day";
import useStyles from "components/DateRangePicker/Header/Header.styles";
import {
  format,
  startOfDay,
  endOfDay,
  addMinutes,
  EN_TIME_FORMAT_HH_MM,
  EN_TIME_FORMAT_A,
  roundTimeToInterval,
  HOURS_PER_DAY,
  AMOUNT_30_MINUTES
} from "utils/datetime";

const IntervalTimeSelectors = ({ value = +new Date(), setValue, stepMinutes = AMOUNT_30_MINUTES }) => {
  const { classes } = useStyles();
  const rounded = roundTimeToInterval(value, stepMinutes);

  // making an array of times with set step, example - for 30 minutes "12:00, 12:30, 1:00, 1:30, ..."
  const times = [];
  const dayStart = startOfDay(+new Date());
  const dayHalf = subHours(endOfDay(dayStart), HOURS_PER_DAY / 2);
  for (let time = dayStart; time < dayHalf; time = addMinutes(time, stepMinutes)) {
    times.push(format(time, EN_TIME_FORMAT_HH_MM));
  }

  const [currentTime, setCurrentTime] = useState(() => format(rounded, EN_TIME_FORMAT_HH_MM));

  // array of AM/PM
  const ampm = [format(dayStart, EN_TIME_FORMAT_A), format(endOfDay(dayStart), EN_TIME_FORMAT_A)];
  const [currentAMPM, setCurrentAMPM] = useState(() => format(rounded, EN_TIME_FORMAT_A));

  const updateSelectedTimestamp = (time, ampmValue) => {
    const selectedTimeString = `${time} ${ampmValue}`;
    const selectedTimeStringFormat = `${EN_TIME_FORMAT_HH_MM} ${EN_TIME_FORMAT_A}`;
    setValue(+parse(selectedTimeString, selectedTimeStringFormat, value));
  };

  const onSelectTime = (event) => {
    setCurrentTime(event.target.value);

    updateSelectedTimestamp(event.target.value, currentAMPM);
  };

  const onSelectAmPm = (ampmValue) => {
    setCurrentAMPM(ampmValue);

    updateSelectedTimestamp(currentTime, ampmValue);
  };

  return (
    <>
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center" }} className={classes.wrapper}>
        <Select
          className={classes.root}
          value={currentTime}
          onChange={onSelectTime}
          inputProps={{ "data-test-id": "half-hour-time-selector" }}
        >
          {times.map((val) => (
            <MenuItem key={val} value={val} disabled={false}>
              {val}
            </MenuItem>
          ))}
        </Select>
      </div>
      <div style={{ display: "flex", justifyContent: "center", padding: "5px" }}>
        {ampm.map((daytimeName) => (
          <Day
            key={daytimeName}
            outlined={currentAMPM === daytimeName}
            filled={currentAMPM === daytimeName}
            onClick={() => onSelectAmPm(daytimeName)}
            value={daytimeName}
          />
        ))}
      </div>
    </>
  );
};

IntervalTimeSelectors.propTypes = {
  value: PropTypes.number,
  setValue: PropTypes.func,
  stepMinutes: PropTypes.number
};

export default IntervalTimeSelectors;

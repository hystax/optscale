import { useState } from "react";
import { Select, MenuItem } from "@mui/material";
import { parse } from "date-fns";
import Day from "components/DateRangePicker/Day";
import useStyles from "components/DateRangePicker/Header/Header.styles";
import {
  format,
  EN_TIME_FORMAT_12_HOURS_CLOCK_HH_MM,
  EN_TIME_FORMAT_A,
  roundTimeToInterval,
  AMOUNT_30_MINUTES,
  generateDayHours,
  MERIDIEM_NAMES
} from "utils/datetime";

const IntervalTimeSelectors = ({ value = +new Date(), setValue, stepMinutes = AMOUNT_30_MINUTES }) => {
  const { classes } = useStyles();
  const rounded = roundTimeToInterval(value, stepMinutes);

  const times = generateDayHours({ stepMinutes });

  const [currentTime, setCurrentTime] = useState(() => format(rounded, EN_TIME_FORMAT_12_HOURS_CLOCK_HH_MM));

  const [currentAMPM, setCurrentAMPM] = useState(() => format(rounded, EN_TIME_FORMAT_A));

  const updateSelectedTimestamp = (time, ampmValue) => {
    const selectedTimeString = `${time} ${ampmValue}`;
    const selectedTimeStringFormat = `${EN_TIME_FORMAT_12_HOURS_CLOCK_HH_MM} ${EN_TIME_FORMAT_A}`;
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
        {Object.values(MERIDIEM_NAMES).map((daytimeName) => (
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

export default IntervalTimeSelectors;

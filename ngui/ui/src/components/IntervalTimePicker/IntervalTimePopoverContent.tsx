import { useState, useRef, useEffect } from "react";
import { Grid } from "@mui/material";
import useStyles from "components/DateRangePicker/DateRangePicker/DateRangePicker.styles";
import Month from "components/DateRangePicker/Month";
import {
  addMonths,
  getTime,
  differenceInCalendarMonths,
  parseOptionalDate,
  MIN_PICKER_DATE,
  AMOUNT_30_MINUTES,
  getHours,
  setHours,
  getMinutes,
  setMinutes,
  roundTimeToInterval,
  subMinutes
} from "utils/datetime";
import IntervalTimeSelectors from "./IntervalTimeSelectors";

// TODO: here and in RangePicker — apply more descriptive naming for whole pickers structure
const IntervalTimePopoverContent = ({
  open,
  onDayClick,
  initialDate = +new Date(),
  minDate,
  maxDate,
  intervalMinutes = AMOUNT_30_MINUTES,
  withTimePicker = false
}) => {
  const { classes, cx } = useStyles();
  const today = new Date();

  const initialDateRounded =
    /**
     * Round to the farthest minute to prevent date jumping to the next day
     * E.g if the initial datetime is equal to "23:59" and intervalMinutes is set to "30"
     * it should be rounded to 23:30, not to 00:00 of the next day
     */
    getHours(initialDate) === 23
      ? roundTimeToInterval(subMinutes(initialDate, intervalMinutes), intervalMinutes)
      : roundTimeToInterval(initialDate, intervalMinutes);

  const minDateValid = parseOptionalDate(minDate, MIN_PICKER_DATE);
  const maxDateValid = parseOptionalDate(maxDate, today);
  const initialFirstMonth = initialDateRounded;

  const [date, setDate] = useState(initialDateRounded);
  const [monthToShow, setMonthToShow] = useState(getTime(initialFirstMonth || today));

  // handlers
  // set month to show from header selectors
  const setMonthToShowValidated = (newDate) => {
    setMonthToShow(newDate);
  };

  // on mount instantly calling callback with rounded time as selected
  const initialMount = useRef(true);
  useEffect(() => {
    if (initialMount.current) {
      initialMount.current = false;
      onDayClick(initialDateRounded);
    }
  });

  // set clicked day — applying rounded hours and minutes to selected date (Month returns start of the day)
  const onDayClickHandler = (day) => {
    const initialDateHours = +getHours(initialDateRounded);
    const initialDateMinutes = +getMinutes(initialDateRounded);

    const dateWithInitialTime = setHours(setMinutes(day, initialDateMinutes), initialDateHours);

    setDate(day);
    onDayClick(dateWithInitialTime);
  };

  const onTimeClickHandler = (day) => {
    setDate(day);
    onDayClick(day);
  };

  // set month to show from header buttons
  const onMonthNavigate = (_, action) => {
    setMonthToShow(getTime(addMonths(monthToShow, action)));
  };

  const onDayHover = () => {};

  // helpers
  const inHoverRange = () => false;

  const helpers = {
    inHoverRange
  };

  const handlers = {
    onDayClick: onDayClickHandler,
    onDayHover,
    onMonthNavigate
  };

  const canNavigatePast = differenceInCalendarMonths(monthToShow, minDateValid) >= 1;
  const canNavigateFuture = differenceInCalendarMonths(maxDateValid, monthToShow) >= 1;

  return open ? (
    <Grid container direction="row" className={classes.wrapper}>
      <Grid item>
        <Grid container direction="row" justifyContent="center">
          <Month
            dateRange={{ startDate: date || false, endDate: date || false }}
            minDate={getTime(minDateValid)}
            maxDate={getTime(maxDateValid)}
            helpers={helpers}
            handlers={handlers}
            value={monthToShow}
            setValue={setMonthToShowValidated}
            navState={[canNavigatePast, canNavigateFuture]}
            marker={1}
            userBounds={{
              minDate: getTime(minDateValid),
              maxDate: getTime(maxDateValid)
            }}
            dataTestIds={{
              monthSelector: "selector_previous_month",
              yearSelector: "selector_previous_year",
              btnPrev: "btn_previous_left",
              btnNext: "btn_previous_right"
            }}
          />
        </Grid>
      </Grid>
      {withTimePicker && (
        <>
          <div className={classes.divider} />
          <span className={cx(classes.wrapper, classes.selectors)}>
            <IntervalTimeSelectors value={date} setValue={onTimeClickHandler} stepMinutes={intervalMinutes} />
          </span>
        </>
      )}
    </Grid>
  ) : null;
};

export default IntervalTimePopoverContent;

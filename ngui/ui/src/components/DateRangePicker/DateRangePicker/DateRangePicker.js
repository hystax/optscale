import React, { useState } from "react";
import { Grid } from "@mui/material";
// TODO - see todo on optional time conversion in datetime util
import PropTypes from "prop-types";
import {
  addMonths,
  isSameDay,
  isWithinInterval,
  isAfter,
  isBefore,
  min,
  max,
  getTime,
  isSameMonth,
  differenceInCalendarMonths,
  getValidatedMonths,
  getMinPickerDateSec,
  getMaxPickerDateSec,
  startOfDay,
  endOfDay,
  subMonths,
  secondsToMilliseconds,
  moveDateFromUTC,
  moveDateToUTC,
  isToday as isTodayDateFNS
} from "utils/datetime";
import { objectMap } from "utils/objects";
import { getBasicRangesSet } from "../defaults";
import DefinedRanges from "../DefinedRanges";
import Month from "../Month";
import useStyles from "./DateRangePicker.styles";

export const MARKERS = Object.freeze({
  FIRST_MONTH: 1,
  SECOND_MONTH: 2
});

const DateRangePicker = (props) => {
  const { classes } = useStyles();
  const today = new Date();

  const {
    open,
    onChange,
    initialDateRange = {},
    minDate,
    maxDate,
    isUtc = true,
    definedRanges = getBasicRangesSet(isUtc)
  } = props;

  // Month component works only with local dates
  // So we need do 3 transitions:
  // 1) min and max dates set in utc should be used as local
  // 2) initialDateRange should be shifted "to utc"
  // 3) onChange should translate local answers to utc
  // 4) add isToday helper
  // 5) handle predefined ranges differently for onChange and setDateRange

  // #1
  const [minDateValid, maxDateValid] = [minDate || getMinPickerDateSec(isUtc), maxDate || getMaxPickerDateSec(isUtc)].map(
    (timestamp) => (isUtc ? moveDateToUTC(timestamp) : timestamp)
  );

  // #2
  const initialDateRangeUTCProcessed =
    isUtc && initialDateRange.startDate && initialDateRange.endDate // do not format undefined dates (events page "latest", for example)
      ? objectMap(initialDateRange, moveDateToUTC)
      : initialDateRange;
  const [initialFirstMonth, initialSecondMonth] = getValidatedMonths(initialDateRangeUTCProcessed, minDateValid, maxDateValid);

  // #2
  const [dateRange, setDateRange] = useState(initialDateRangeUTCProcessed);
  const [hoverDay, setHoverDay] = useState();
  const [secondMonth, setSecondMonth] = useState(getTime(initialSecondMonth || today));
  const [firstMonth, setFirstMonth] = useState(getTime(initialFirstMonth || subMonths(secondMonth, 1)));

  const { startDate, endDate } = dateRange;

  // handlers
  const setFirstMonthValidated = (date) => {
    if (isBefore(date, secondMonth)) {
      setFirstMonth(date);
    }
  };

  const setSecondMonthValidated = (date) => {
    if (isAfter(date, firstMonth)) {
      setSecondMonth(date);
    }
  };

  const setEmptyRange = () => {
    const emptyRange = {};

    setDateRange(emptyRange);
    onChange(emptyRange);

    setFirstMonth(getTime(subMonths(today, 1)));
    setSecondMonth(getTime(today));
  };

  // before calling external onChange fn we setting start date to start of the day, end date to end of the day
  const onChangeRangeProcessing = (range) => {
    const rangeToStartEndOfDays = { startDate: +startOfDay(range.startDate), endDate: +endOfDay(range.endDate) };

    // #3
    // dates are local. If we want to set them as UTC — just remove timezone offset
    onChange(isUtc ? objectMap(rangeToStartEndOfDays, moveDateFromUTC) : rangeToStartEndOfDays);
  };

  // #5
  // setting value from predefined ranges selector
  const setDateRangeValidated = (range) => {
    const { startDate: newStart, endDate: newEnd } = objectMap(range, secondsToMilliseconds);

    if (!(newStart && newEnd)) {
      setEmptyRange();
      return;
    }

    // min and max date already converted to local time, in defined ranges in utc, need to shift min/max
    const [minBound, maxBound] = [minDateValid, maxDateValid].map((timestamp) =>
      isUtc ? moveDateFromUTC(timestamp) : timestamp
    );

    // fitting start and end into min-max interval of picker
    const maxStartValue = getTime(max([newStart, minBound]));
    const minEndValue = getTime(min([newEnd, maxBound]));

    // if [range] ∪ [min;max] === ∅ — end day will be before start day
    if (isBefore(minEndValue, maxStartValue)) {
      setEmptyRange();
      return;
    }

    // there is something selected, setting ui and calling callback
    const newRange = { startDate: maxStartValue, endDate: minEndValue };
    setDateRange(isUtc ? objectMap(newRange, moveDateToUTC) : newRange); // component state is local
    onChange(newRange); // predefined ranges are passed as they were created, without setting start and end of the day

    // set previous month if range in same month
    setFirstMonth(isSameMonth(maxStartValue, minEndValue) ? getTime(subMonths(minEndValue, 1)) : maxStartValue);
    setSecondMonth(minEndValue);
  };

  const onDayClick = (day) => {
    if (startDate && !endDate) {
      // range must be with smaller date as startDate
      const newRange = isAfter(day, startDate) ? { startDate, endDate: day } : { startDate: day, endDate: startDate };
      onChangeRangeProcessing(newRange);
      setDateRange(newRange);
    } else {
      setDateRange({ startDate: day, endDate: undefined });
    }
    setHoverDay(day);
  };

  const onMonthNavigate = (marker, action) => {
    if (marker === MARKERS.FIRST_MONTH) {
      const firstNew = addMonths(firstMonth, action);
      if (isBefore(firstNew, secondMonth)) {
        setFirstMonth(getTime(firstNew));
      }
    }
    if (marker === MARKERS.SECOND_MONTH) {
      const secondNew = addMonths(secondMonth, action);
      if (isBefore(firstMonth, secondNew)) {
        setSecondMonth(getTime(secondNew));
      }
    }
  };

  const onDayHover = (date) => {
    if (startDate && !endDate) {
      if (!hoverDay || !isSameDay(date, hoverDay)) {
        setHoverDay(date);
      }
    }
  };

  // helpers
  const inHoverRange = (day) => {
    const intervalToCheck = isAfter(hoverDay, startDate)
      ? { start: startDate, end: hoverDay }
      : { start: hoverDay, end: startDate };

    return startDate && !endDate && hoverDay && isWithinInterval(day, intervalToCheck);
  };

  // #4
  const isToday = (day) => (isUtc ? isSameDay(day, moveDateToUTC(new Date())) : isTodayDateFNS(day));

  const helpers = {
    inHoverRange,
    isToday
  };

  const handlers = {
    onDayClick,
    onDayHover,
    onMonthNavigate
  };

  const canNavigateCloser = differenceInCalendarMonths(secondMonth, firstMonth) >= 2;
  const canNavigatePast = differenceInCalendarMonths(firstMonth, minDateValid) >= 1;
  const canNavigateFuture = differenceInCalendarMonths(maxDateValid, secondMonth) >= 1;

  const commonProps = {
    dateRange,
    minDate: getTime(minDateValid),
    maxDate: getTime(maxDateValid),
    helpers,
    handlers
  };

  return open ? (
    <Grid container direction="row">
      <Grid item>
        <Grid container direction="row" justifyContent="center">
          <Month
            {...commonProps}
            value={firstMonth}
            setValue={setFirstMonthValidated}
            navState={[canNavigatePast, canNavigateCloser]}
            marker={MARKERS.FIRST_MONTH}
            userBounds={{
              minDate: getTime(minDateValid),
              maxDate: getTime(subMonths(secondMonth, 1))
            }}
            dataTestIds={{
              monthSelector: "selector_previous_month",
              yearSelector: "selector_previous_year",
              btnPrev: "btn_previous_left",
              btnNext: "btn_previous_right"
            }}
          />
          <div className={classes.divider} />
          <Month
            {...commonProps}
            value={secondMonth}
            setValue={setSecondMonthValidated}
            navState={[canNavigateCloser, canNavigateFuture]}
            marker={MARKERS.SECOND_MONTH}
            userBounds={{
              minDate: getTime(addMonths(firstMonth, 1)),
              maxDate: getTime(maxDateValid)
            }}
            dataTestIds={{
              monthSelector: "selector_next_month",
              yearSelector: "selector_next_year",
              btnPrev: "btn_next_left",
              btnNext: "btn_next_right"
            }}
          />
        </Grid>
      </Grid>
      <div className={classes.divider} />
      <Grid item>
        {/* DefinedRanges working with ranges as-is, so passing range without any shifts */}
        <DefinedRanges selectedRange={initialDateRange} ranges={definedRanges} setRange={setDateRangeValidated} />
      </Grid>
    </Grid>
  ) : null;
};

const DateType = PropTypes.oneOfType([PropTypes.object, PropTypes.number]);

const DefinedRangesType = PropTypes.arrayOf(
  PropTypes.shape({
    messageId: PropTypes.string,
    key: PropTypes.string,
    startDate: DateType,
    endDate: DateType,
    dataTestId: PropTypes.string
  })
);

DateRangePicker.propTypes = {
  open: PropTypes.bool.isRequired,
  initialDateRange: PropTypes.object,
  definedRanges: DefinedRangesType,
  minDate: DateType,
  maxDate: DateType,
  onChange: PropTypes.func.isRequired,
  isUtc: PropTypes.bool
};

export { DefinedRangesType };
export default DateRangePicker;

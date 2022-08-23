import React from "react";
import { Paper, Grid, Typography } from "@mui/material";
import PropTypes from "prop-types";
import { getChunks } from "utils/arrays";
import {
  SHORT_WEEK_DAYS,
  getDaysInMonth,
  isStartOfRange,
  isEndOfRange,
  inDateRange,
  isRangeSameDay,
  getDate,
  isSameMonth,
  isToday,
  isWithinInterval
} from "utils/datetime";
import Day from "../Day";
import Header, { BoundsType, HeaderDataTestIdsType } from "../Header";
import useStyles from "./Month.styles";

const Month = (props) => {
  const { classes } = useStyles();

  const {
    helpers,
    handlers,
    value: date,
    dateRange,
    marker,
    setValue: setDate,
    minDate,
    maxDate,
    navState = [],
    userBounds,
    dataTestIds
  } = props;

  const [back, forward] = navState;

  return (
    <Paper square elevation={0} className={classes.root}>
      <Grid container>
        <Header
          date={date}
          yearsFrom={new Date(minDate).getFullYear()}
          yearsTo={new Date(maxDate).getFullYear()}
          setDate={setDate}
          nextDisabled={!forward}
          prevDisabled={!back}
          onClickPrevious={() => handlers.onMonthNavigate(marker, -1)}
          onClickNext={() => handlers.onMonthNavigate(marker, 1)}
          userBounds={userBounds}
          dataTestIds={dataTestIds}
        />
        <Grid item container direction="row" justifyContent="space-between" className={classes.weekDaysContainer}>
          {SHORT_WEEK_DAYS.map((day) => (
            <Typography key={day} variant="caption">
              {day}
            </Typography>
          ))}
        </Grid>
        <Grid item container direction="column" justifyContent="space-between" className={classes.daysContainer}>
          {getChunks(getDaysInMonth(date), 7).map((week) => (
            <Grid key={JSON.stringify(`${week[0]}`)} container direction="row" justifyContent="center">
              {week.map((day) => {
                const isStart = isStartOfRange(dateRange, day);
                const isEnd = isEndOfRange(dateRange, day);
                const isRangeOneDay = isRangeSameDay(dateRange);
                const highlighted = inDateRange(dateRange, day) || helpers.inHoverRange(day);
                return (
                  <Day
                    key={JSON.stringify(`${day}`)}
                    filled={isStart || isEnd}
                    outlined={typeof helpers.isToday === "function" ? helpers.isToday(day) : isToday(day)}
                    highlighted={highlighted && !isRangeOneDay}
                    disabled={!isSameMonth(date, day) || !isWithinInterval(day, { start: minDate, end: maxDate })}
                    onClick={() => handlers.onDayClick(day)}
                    onHover={() => handlers.onDayHover(day)}
                    value={getDate(day)}
                  />
                );
              })}
            </Grid>
          ))}
        </Grid>
      </Grid>
    </Paper>
  );
};

Month.propTypes = {
  dateRange: PropTypes.object.isRequired,
  marker: PropTypes.number.isRequired,
  value: PropTypes.number.isRequired,
  minDate: PropTypes.number.isRequired,
  maxDate: PropTypes.number.isRequired,
  navState: PropTypes.array.isRequired,
  setValue: PropTypes.func.isRequired,
  helpers: PropTypes.shape({
    inHoverRange: PropTypes.func.isRequired,
    isToday: PropTypes.func
  }),
  handlers: PropTypes.shape({
    onDayClick: PropTypes.func.isRequired,
    onDayHover: PropTypes.func.isRequired,
    onMonthNavigate: PropTypes.func.isRequired
  }),
  userBounds: BoundsType,
  dataTestIds: HeaderDataTestIdsType
};

export default Month;

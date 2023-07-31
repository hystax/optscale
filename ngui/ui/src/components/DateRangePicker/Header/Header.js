import React, { useState } from "react";
import ChevronLeft from "@mui/icons-material/ChevronLeft";
import ChevronRight from "@mui/icons-material/ChevronRight";
import { Grid, IconButton, Select, MenuItem } from "@mui/material";
import PropTypes from "prop-types";
import {
  SHORT_MONTHS,
  generateYears,
  setMonth,
  getMonth,
  setYear,
  getYear,
  getTime,
  endOfYear,
  isAfter,
  startOfYear,
  isWithinInterval,
  startOfMonth,
  endOfMonth,
  fitDateIntoInterval
} from "utils/datetime";
import useStyles from "./Header.styles";

const Header = ({
  date,
  yearsFrom,
  yearsTo,
  setDate,
  nextDisabled,
  prevDisabled,
  onClickNext,
  onClickPrevious,
  userBounds: { minDate: rowMinDate, maxDate: rowMaxDate },
  dataTestIds = {}
}) => {
  const { classes } = useStyles();

  const minDate = getTime(startOfMonth(rowMinDate));
  const maxDate = getTime(endOfMonth(rowMaxDate));
  const {
    monthSelector: monthDataTestId,
    yearSelector: yearDataTestId,
    btnPrev: btnPrevDataTestId,
    btnNext: btnNextDataTestId
  } = dataTestIds;

  const [years] = useState(generateYears(yearsTo, yearsFrom));

  // todo: move to utils/datetime.js — after ms/s codebase refactoring https://datatrendstech.atlassian.net/browse/NGUI-2948
  const getMonthValue = (month) => getTime(setMonth(date, month));
  const getYearValue = (year) => getTime(setYear(date, year));

  const handleMonthChange = (event) => {
    setDate(getMonthValue(event.target.value));
  };

  const handleYearChange = (event) => {
    // year from selector combined with month could be out of bounds — setting min or max value if so
    const dateThatYear = getYearValue(event.target.value);

    const dateFromInterval = fitDateIntoInterval({ minDate, maxDate, date: dateThatYear });
    setDate(dateFromInterval);
  };

  const isMonthOutOfBounds = (dateToCheck) =>
    !(isAfter(maxDate, minDate) && isWithinInterval(dateToCheck, { start: minDate, end: maxDate }));

  const isYearOutOfBounds = (yearToCheck) => {
    const dateThatYear = getYearValue(yearToCheck);

    return (
      isAfter(maxDate, minDate) && !isWithinInterval(dateThatYear, { start: startOfYear(minDate), end: endOfYear(maxDate) })
    );
  };

  return (
    <Grid container justifyContent="space-between" alignItems="center" className={classes.wrapper}>
      <Grid item>
        <IconButton disabled={prevDisabled} onClick={onClickPrevious} data-test-id={btnPrevDataTestId}>
          <ChevronLeft color={prevDisabled ? "disabled" : "action"} />
        </IconButton>
      </Grid>
      <Grid item>
        {/* TODO: Replaces with Selector after https://gitlab.com/hystax/ngui/-/merge_requests/1823 */}
        <Select
          className={classes.root}
          value={getMonth(date)}
          onChange={handleMonthChange}
          data-test-id={monthDataTestId}
          variant="standard"
        >
          {SHORT_MONTHS.map((month, index) => (
            <MenuItem key={month} value={index} disabled={isMonthOutOfBounds(getMonthValue(index))}>
              {month}
            </MenuItem>
          ))}
        </Select>
      </Grid>
      <Grid item>
        {/* TODO: Replaces with Selector after https://gitlab.com/hystax/ngui/-/merge_requests/1823 */}
        <Select
          className={classes.root}
          value={getYear(date)}
          onChange={handleYearChange}
          data-test-id={yearDataTestId}
          variant="standard"
        >
          {years.map((year) => (
            <MenuItem key={year} value={year} disabled={isYearOutOfBounds(year)}>
              {year}
            </MenuItem>
          ))}
        </Select>
      </Grid>
      <Grid item>
        <IconButton disabled={nextDisabled} onClick={onClickNext} data-test-id={btnNextDataTestId}>
          <ChevronRight color={nextDisabled ? "disabled" : "action"} />
        </IconButton>
      </Grid>
    </Grid>
  );
};

export const BoundsType = PropTypes.shape({
  minDate: PropTypes.number,
  maxDate: PropTypes.number
});

export const HeaderDataTestIdsType = PropTypes.shape({
  monthSelector: PropTypes.string,
  yearSelector: PropTypes.string,
  btnPrev: PropTypes.string,
  btnNext: PropTypes.string
});

Header.propTypes = {
  date: PropTypes.number.isRequired,
  yearsFrom: PropTypes.number.isRequired,
  yearsTo: PropTypes.number.isRequired,
  setDate: PropTypes.func.isRequired,
  nextDisabled: PropTypes.bool.isRequired,
  prevDisabled: PropTypes.bool.isRequired,
  onClickNext: PropTypes.func.isRequired,
  onClickPrevious: PropTypes.func.isRequired,
  userBounds: BoundsType,
  dataTestIds: HeaderDataTestIdsType
};

export default Header;

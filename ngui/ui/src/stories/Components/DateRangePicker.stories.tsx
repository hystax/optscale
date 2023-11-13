import { useState } from "react";
import DateRangePicker from "components/DateRangePicker";
import { KINDS } from "stories";
import { startOfDay, endOfDay } from "utils/datetime";

export default {
  title: `${KINDS.COMPONENTS}/DateRangePicker`
};

const DateRange = ({ pickerProps = {} }) => {
  const [open, setOpen] = useState(true);
  const [dateRange, setDateRange] = useState({});

  const toggle = () => setOpen(!open);

  return (
    <>
      <DateRangePicker open={open} toggle={toggle} onChange={(range) => setDateRange(range)} {...pickerProps} />
      <p>Start date human readable: {dateRange.startDate && new Date(dateRange.startDate).toUTCString()}</p>
      <p>Start date timestamp: {dateRange.startDate}</p>
      <br />
      <p>End date human readable: {dateRange.endDate && new Date(dateRange.endDate).toUTCString()}</p>
      <p>End date timestamp: {dateRange.endDate}</p>
    </>
  );
};

const DateRangeBasic = () => <DateRange />;

const DateRangeLimited = () => <DateRange pickerProps={{ minDate: startOfDay(new Date()), maxDate: endOfDay(new Date()) }} />;

export const limitedToToday = () => <DateRangeLimited />;

export const basic = () => <DateRangeBasic />;

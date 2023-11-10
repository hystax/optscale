import { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";
import {
  endOfDay,
  formatRangeToShortNotation,
  getMaxPickerDateMsec,
  getMinPickerDateSec,
  millisecondsToSeconds,
  performDateTimeFunction,
  secondsToMilliseconds,
  startOfDay,
  subDays
} from "utils/datetime";
import { getQueryParams, updateQueryParams } from "utils/network";

const allRange = (isUtc) => ({
  type: "all",
  isUtc,
  getInterval: () => ({
    startDate: secondsToMilliseconds(getMinPickerDateSec(isUtc)),
    endDate: getMaxPickerDateMsec(isUtc)
  }),
  getName: () => <FormattedMessage id="all" />,
  getSearchParams: () => ({
    period: "all",
    startDate: undefined,
    endDate: undefined
  }),
  isDefaultByQueryParams: () => {
    const queryParams = getQueryParams();
    return queryParams.period === "all";
  },
  init() {
    return {
      name: this.getName(),
      interval: this.getInterval(),
      searchParams: this.getSearchParams()
    };
  }
});

const oneDayRange = (isUtc) => ({
  type: "1day",
  isUtc,
  getInterval: () => ({
    startDate: performDateTimeFunction(startOfDay, isUtc, +new Date()),
    endDate: performDateTimeFunction(endOfDay, isUtc, +new Date())
  }),
  getName: () => <FormattedMessage id="xDays" values={{ x: 1 }} />,
  getSearchParams: () => ({
    period: "1day",
    startDate: undefined,
    endDate: undefined
  }),
  isDefaultByQueryParams: () => {
    const queryParams = getQueryParams();
    return queryParams.period === "1day";
  },
  init() {
    return {
      name: this.getName(),
      interval: this.getInterval(),
      searchParams: this.getSearchParams()
    };
  }
});

const oneWeekRange = (isUtc) => ({
  type: "1week",
  isUtc,
  getInterval: () => {
    const startOfToday = performDateTimeFunction(startOfDay, isUtc, +new Date());

    return {
      startDate: performDateTimeFunction(subDays, isUtc, startOfToday, 6),
      endDate: performDateTimeFunction(endOfDay, isUtc, +new Date())
    };
  },
  getName: () => <FormattedMessage id="xWeeks" values={{ x: 1 }} />,
  getSearchParams: () => ({
    period: "1week",
    startDate: undefined,
    endDate: undefined
  }),
  isDefaultByQueryParams: () => {
    const queryParams = getQueryParams();
    return queryParams.period === "1week";
  },
  init() {
    return {
      name: this.getName(),
      interval: this.getInterval(),
      searchParams: this.getSearchParams()
    };
  }
});

const twoWeeksRange = (isUtc) => ({
  type: "2weeks",
  isUtc,
  getInterval: () => {
    const startOfToday = performDateTimeFunction(startOfDay, isUtc, +new Date());

    return {
      startDate: performDateTimeFunction(subDays, isUtc, startOfToday, 13),
      endDate: performDateTimeFunction(endOfDay, isUtc, +new Date())
    };
  },
  getName: () => <FormattedMessage id="xWeeks" values={{ x: 2 }} />,
  getSearchParams: () => ({
    period: "2weeks",
    startDate: undefined,
    endDate: undefined
  }),
  isDefaultByQueryParams: () => {
    const queryParams = getQueryParams();
    return queryParams.period === "2weeks";
  },
  init() {
    return {
      name: this.getName(),
      interval: this.getInterval(),
      searchParams: this.getSearchParams()
    };
  }
});

const oneMonthRange = (isUtc) => ({
  type: "1month",
  isUtc,
  getInterval: () => {
    const startOfToday = performDateTimeFunction(startOfDay, isUtc, +new Date());

    return {
      startDate: performDateTimeFunction(subDays, isUtc, startOfToday, 29),
      endDate: performDateTimeFunction(endOfDay, isUtc, +new Date())
    };
  },
  getName: () => <FormattedMessage id="xMonth" values={{ x: 1 }} />,
  getSearchParams: () => ({
    period: "1month",
    startDate: undefined,
    endDate: undefined
  }),
  isDefaultByQueryParams: () => {
    const queryParams = getQueryParams();
    return queryParams.period === "1month";
  },
  init() {
    return {
      name: this.getName(),
      interval: this.getInterval(),
      searchParams: this.getSearchParams()
    };
  }
});

const customRange = (isUtc) => ({
  type: "custom",
  isUtc,
  getName(millisecondsStartDate, millisecondsEndDate) {
    return formatRangeToShortNotation(
      millisecondsToSeconds(millisecondsStartDate),
      millisecondsToSeconds(millisecondsEndDate),
      isUtc
    );
  },
  getInterval: (millisecondsStartDate, millisecondsEndDate) => ({
    startDate: millisecondsStartDate,
    endDate: millisecondsEndDate
  }),
  getSearchParams: (millisecondsStartDate, millisecondsEndDate) => ({
    startDate: millisecondsToSeconds(millisecondsStartDate),
    endDate: millisecondsToSeconds(millisecondsEndDate),
    period: undefined
  }),
  isDefaultByQueryParams: () => {
    const queryParams = getQueryParams();
    return queryParams.startDate && queryParams.endDate;
  },
  init() {
    const queryParams = getQueryParams();
    const numberStartDate = parseInt(queryParams.startDate, 10);
    const numberEndDate = parseInt(queryParams.endDate, 10);

    if (Number.isNaN(numberStartDate) || Number.isNaN(numberEndDate) || numberStartDate > numberEndDate) {
      const millisecondsStartDate = secondsToMilliseconds(getMinPickerDateSec(isUtc));
      const millisecondsEndDate = getMaxPickerDateMsec(isUtc);
      return {
        name: this.getName(millisecondsStartDate, millisecondsEndDate),
        interval: this.getInterval(millisecondsStartDate, millisecondsEndDate),
        searchParams: this.getSearchParams(millisecondsStartDate, millisecondsEndDate)
      };
    }

    const startDate = performDateTimeFunction(startOfDay, isUtc, secondsToMilliseconds(numberStartDate));
    const endDate = performDateTimeFunction(endOfDay, isUtc, secondsToMilliseconds(numberEndDate));

    return {
      name: this.getName(startDate, endDate),
      interval: this.getInterval(startDate, endDate),
      searchParams: this.getSearchParams(startDate, endDate)
    };
  }
});

const useDateRanges = (ranges) => {
  const [selectedRange, setSelectedRange] = useState(() => {
    const defaultByQueryParamsRange = ranges.find((rg) => rg.isDefaultByQueryParams());

    if (defaultByQueryParamsRange) {
      return defaultByQueryParamsRange.init();
    }

    return ranges[0].init();
  });

  useEffect(() => {
    updateQueryParams(selectedRange.searchParams);
  }, [selectedRange]);

  return {
    selectedRange,
    onSelectedRangeChange: ({ name, interval, searchParams }) => {
      setSelectedRange({
        name,
        interval,
        searchParams
      });
    },
    ranges: ranges.map(({ type, isUtc, getInterval, getName, getSearchParams }) => ({
      type,
      isUtc,
      getInterval,
      getName,
      getSearchParams
    }))
  };
};

export default useDateRanges;

export { allRange, oneDayRange, oneWeekRange, twoWeeksRange, oneMonthRange, customRange };

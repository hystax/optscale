import { createGroupsObjectFromArray, splitIntoChunks } from "utils/arrays";
import { WEEK_LENGTH } from "utils/constants";
import {
  secondsToMilliseconds,
  millisecondsToSeconds,
  formatUTC,
  EN_FORMAT_SHORT_YEAR,
  startOfDay,
  endOfDay,
  performDateTimeFunction
} from "utils/datetime";

const startOfDayInUTC = (timestamp) =>
  millisecondsToSeconds(performDateTimeFunction(startOfDay, true, secondsToMilliseconds(timestamp)));
const endOfDayInUTC = (timestamp) =>
  millisecondsToSeconds(performDateTimeFunction(endOfDay, true, secondsToMilliseconds(timestamp)));

const groupChunkBreakdownArray = (chunk, dates) =>
  Object.values(
    chunk.reduce((groupedData, [, breakdownArray]) => {
      if (Array.isArray(breakdownArray)) {
        const mergedData = { ...groupedData };
        breakdownArray.forEach((obj) => {
          mergedData[obj.name] = {
            ...(mergedData[obj.name] ?? {}),
            ...obj,
            startDate: dates.startDate,
            endDate: dates.endDate,
            expense: (mergedData[obj.name]?.expense ?? 0) + obj.expense
          };
        });
        return mergedData;
      }
      return groupedData;
    }, {})
  );

const getChunkTimeInterval = (chunk) => {
  const sStartTimestamp = Number(chunk[0][0]);
  const sEndTimestamp = Number(chunk[chunk.length - 1][0]);

  const start = startOfDayInUTC(sStartTimestamp);
  const end = endOfDayInUTC(sEndTimestamp);

  return {
    start,
    end
  };
};

const getDailyBreakdownData = (breakdown) =>
  Object.fromEntries(
    Object.entries(breakdown).map(([sTimestamp, expense]) => [
      formatUTC(sTimestamp, EN_FORMAT_SHORT_YEAR),
      expense.map((e) => ({
        ...e,
        startDate: startOfDayInUTC(sTimestamp),
        endDate: endOfDayInUTC(sTimestamp)
      }))
    ])
  );

const getWeeklyBreakdownData = (breakdown) =>
  Object.fromEntries(
    splitIntoChunks(Object.entries(breakdown), WEEK_LENGTH).map((weeklyChunk) => {
      const { start, end } = getChunkTimeInterval(weeklyChunk);

      const groupArray = groupChunkBreakdownArray(weeklyChunk, {
        startDate: start,
        endDate: end
      });

      const formattedStartDate = formatUTC(start, EN_FORMAT_SHORT_YEAR);
      const formattedEndDate = formatUTC(end, EN_FORMAT_SHORT_YEAR);

      return [weeklyChunk.length === 1 ? `${formattedStartDate}` : `${formattedStartDate} - ${formattedEndDate}`, groupArray];
    })
  );

const getMonthlyBreakdownData = (breakdown) => {
  const groupedByMonthBreakdown = createGroupsObjectFromArray(Object.entries(breakdown), ([date]) =>
    formatUTC(date, "MMM, yyyy")
  );

  return Object.fromEntries(
    Object.entries(groupedByMonthBreakdown).map(([groupName, monthlyChunkData]) => {
      const { start, end } = getChunkTimeInterval(monthlyChunkData);

      const groupArray = groupChunkBreakdownArray(monthlyChunkData, {
        startDate: start,
        endDate: end
      });

      return [groupName, groupArray];
    })
  );
};

export const useBreakdownData = (breakdown) => {
  const dailyBreakdownData = getDailyBreakdownData(breakdown);

  const weeklyBreakdownData = getWeeklyBreakdownData(breakdown);

  const monthlyBreakdownData = getMonthlyBreakdownData(breakdown);

  return {
    daily: dailyBreakdownData,
    weekly: weeklyBreakdownData,
    monthly: monthlyBreakdownData
  };
};

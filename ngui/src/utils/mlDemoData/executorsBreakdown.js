import { ML_EXECUTORS_DAILY_BREAKDOWN_BY } from "utils/constants";
import { startOfDay, millisecondsToSeconds, subDays, addDays } from "utils/datetime";

const start = 1674676800000;

const executorsBreakdown = {
  [ML_EXECUTORS_DAILY_BREAKDOWN_BY.CPU]: {
    [millisecondsToSeconds(startOfDay(subDays(start, 3)))]: 5,
    [millisecondsToSeconds(startOfDay(subDays(start, 2)))]: 9,
    [millisecondsToSeconds(startOfDay(subDays(start, 1)))]: 11,
    [millisecondsToSeconds(start)]: 19,
    [millisecondsToSeconds(startOfDay(addDays(start, 1)))]: 20,
    [millisecondsToSeconds(startOfDay(addDays(start, 2)))]: 13,
    [millisecondsToSeconds(startOfDay(addDays(start, 3)))]: 14,
    [millisecondsToSeconds(startOfDay(addDays(start, 4)))]: 15,
    [millisecondsToSeconds(startOfDay(addDays(start, 5)))]: 11
  },
  [ML_EXECUTORS_DAILY_BREAKDOWN_BY.RAM]: {
    [millisecondsToSeconds(startOfDay(subDays(start, 3)))]: 970,
    [millisecondsToSeconds(startOfDay(subDays(start, 2)))]: 1190,
    [millisecondsToSeconds(startOfDay(subDays(start, 1)))]: 1160,
    [millisecondsToSeconds(start)]: 1280,
    [millisecondsToSeconds(startOfDay(addDays(start, 1)))]: 500,
    [millisecondsToSeconds(startOfDay(addDays(start, 2)))]: 630,
    [millisecondsToSeconds(startOfDay(addDays(start, 3)))]: 430,
    [millisecondsToSeconds(startOfDay(addDays(start, 4)))]: 512,
    [millisecondsToSeconds(startOfDay(addDays(start, 5)))]: 800
  },
  [ML_EXECUTORS_DAILY_BREAKDOWN_BY.EXECUTORS_COUNT]: {
    [millisecondsToSeconds(startOfDay(subDays(start, 3)))]: 2,
    [millisecondsToSeconds(startOfDay(subDays(start, 2)))]: 1,
    [millisecondsToSeconds(startOfDay(subDays(start, 1)))]: 1,
    [millisecondsToSeconds(start)]: 2,
    [millisecondsToSeconds(startOfDay(addDays(start, 1)))]: 2,
    [millisecondsToSeconds(startOfDay(addDays(start, 2)))]: 1,
    [millisecondsToSeconds(startOfDay(addDays(start, 3)))]: 3,
    [millisecondsToSeconds(startOfDay(addDays(start, 4)))]: 3,
    [millisecondsToSeconds(startOfDay(addDays(start, 5)))]: 2
  },
  [ML_EXECUTORS_DAILY_BREAKDOWN_BY.PROCESS_CPU]: {
    [millisecondsToSeconds(startOfDay(subDays(start, 3)))]: 20,
    [millisecondsToSeconds(startOfDay(subDays(start, 2)))]: 25,
    [millisecondsToSeconds(startOfDay(subDays(start, 1)))]: 24,
    [millisecondsToSeconds(start)]: 23,
    [millisecondsToSeconds(startOfDay(addDays(start, 1)))]: 51,
    [millisecondsToSeconds(startOfDay(addDays(start, 2)))]: 52,
    [millisecondsToSeconds(startOfDay(addDays(start, 3)))]: 32,
    [millisecondsToSeconds(startOfDay(addDays(start, 4)))]: 25,
    [millisecondsToSeconds(startOfDay(addDays(start, 5)))]: 20
  },
  [ML_EXECUTORS_DAILY_BREAKDOWN_BY.PROCESS_RAM]: {
    [millisecondsToSeconds(startOfDay(subDays(start, 3)))]: 122,
    [millisecondsToSeconds(startOfDay(subDays(start, 2)))]: 125,
    [millisecondsToSeconds(startOfDay(subDays(start, 1)))]: 175,
    [millisecondsToSeconds(start)]: 178,
    [millisecondsToSeconds(startOfDay(addDays(start, 1)))]: 180,
    [millisecondsToSeconds(startOfDay(addDays(start, 2)))]: 230,
    [millisecondsToSeconds(startOfDay(addDays(start, 3)))]: 200,
    [millisecondsToSeconds(startOfDay(addDays(start, 4)))]: 150,
    [millisecondsToSeconds(startOfDay(addDays(start, 5)))]: 125
  }
};

export { executorsBreakdown };

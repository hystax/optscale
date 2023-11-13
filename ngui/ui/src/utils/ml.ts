import { isEmpty as isEmptyArray } from "./arrays";
import { GOAL_STATUS, GOALS_FILTER_TYPES } from "./constants";

export const formatRunNumber = (number) => `#${number}`;

export const formatRunFullName = (number, name) => `${formatRunNumber(number)}_${name}`;

export const getRunsGoalsKeyNameEntries = (runs) =>
  isEmptyArray(runs) ? [] : Object.entries(runs[0].reached_goals).map(([key, { name }]) => [key, name]);

export const getModelsGoalsKeyNameEntries = (models) => {
  const goalsMap = new Map(models.flatMap((model) => model.run_goals.map(({ key, name }) => [key, name])));

  return Array.from(goalsMap.entries());
};

export const getFirstGoalEntryKey = (entries = []) => entries[0]?.[0];

export const getGoalStatus = (value, targetValue, tendency) => {
  if (tendency === GOALS_FILTER_TYPES.LESS_IS_BETTER) {
    return value <= targetValue ? GOAL_STATUS.MET : GOAL_STATUS.NOT_MET;
  }

  return value >= targetValue ? GOAL_STATUS.MET : GOAL_STATUS.NOT_MET;
};

export const getGoalsStatus = (goals) => {
  const areAllGoalsMet = () =>
    goals.every(({ value, targetValue, tendency }) => getGoalStatus(value, targetValue, tendency) === GOAL_STATUS.MET);

  if (areAllGoalsMet(goals)) {
    return GOAL_STATUS.MET;
  }
  return GOAL_STATUS.NOT_MET;
};

import { SHORT_WEEK_DAYS } from "utils/datetime";
import { useOrganizationFeatures } from "./useOrganizationFeatures";

export const getValidCustomWeekends = (customWeekends) => {
  if (Array.isArray(customWeekends)) {
    const filteredCustomWeekends = customWeekends.filter((value) => SHORT_WEEK_DAYS.includes(value));

    if (filteredCustomWeekends.length !== 0) {
      return [...new Set(filteredCustomWeekends)];
    }
  }

  return [SHORT_WEEK_DAYS[0], SHORT_WEEK_DAYS[6]];
};

export const useCustomOrganizationWeekends = () => {
  const { custom_weekends: customWeekends } = useOrganizationFeatures();

  const customWeekendNames = getValidCustomWeekends(customWeekends);

  return {
    names: customWeekendNames,
    indexes: customWeekendNames.map((name) => SHORT_WEEK_DAYS.indexOf(name))
  };
};

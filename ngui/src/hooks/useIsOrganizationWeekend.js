import { useCustomOrganizationWeekends } from "./useCustomOrganizationWeekends";

export const useIsOrganizationWeekend = () => {
  const { indexes: customWeekendIndexes } = useCustomOrganizationWeekends();

  return (date) => {
    const day = date.getDay();

    return customWeekendIndexes.includes(day);
  };
};

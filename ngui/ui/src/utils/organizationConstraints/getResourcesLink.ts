import { getLink } from "./getLink";
import { getResourcesDateRange } from "./getResourcesDateRange";

export const getResourcesLink = (constraint) => {
  const dateRange = getResourcesDateRange(constraint);

  return getLink({
    dateRange,
    constraint,
  });
};

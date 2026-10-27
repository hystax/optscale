import { getConstraintHitResourcesDateRange } from "./getConstraintHitResourcesDateRange";
import { getLink } from "./getLink";

export const getConstraintHitResourcesLink = (hitDate, constraint) => {
  const dateRange = getConstraintHitResourcesDateRange(hitDate, constraint);

  return getLink({
    dateRange,
    constraint,
  });
};

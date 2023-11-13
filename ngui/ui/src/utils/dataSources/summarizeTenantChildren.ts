import { isEmpty } from "utils/arrays";

export const summarizeChildrenDetails = (children) =>
  isEmpty(children)
    ? {}
    : children.reduce(
        (acc, { details: { tracked = 0, cost = 0, forecast = 0, last_month_cost: lastMonthCost = 0 } = {} }) => ({
          tracked: acc.tracked + tracked,
          cost: acc.cost + cost,
          forecast: acc.forecast + forecast,
          last_month_cost: acc.last_month_cost + lastMonthCost
        }),
        {
          tracked: 0,
          cost: 0,
          forecast: 0,
          last_month_cost: 0
        }
      );

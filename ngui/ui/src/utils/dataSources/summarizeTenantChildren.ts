import { isEmptyArray } from "utils/arrays";

export const summarizeChildrenDetails = (children) =>
  isEmptyArray(children)
    ? {}
    : children.reduce(
        (acc, { details: { resources = 0, cost = 0, forecast = 0, last_month_cost: lastMonthCost = 0 } = {} }) => ({
          resources: acc.resources + resources,
          cost: acc.cost + cost,
          forecast: acc.forecast + forecast,
          last_month_cost: acc.last_month_cost + lastMonthCost,
        }),
        {
          resources: 0,
          cost: 0,
          forecast: 0,
          last_month_cost: 0,
        }
      );

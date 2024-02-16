export const isCostOverLimit = ({ limit, cost }) => limit > 0 && limit < cost;

export const isForecastOverLimit = ({ limit, forecast }) => limit > 0 && limit < forecast;

// A condition when a pool is considered limited
export const hasLimit = (limit?: number) => limit !== 0;

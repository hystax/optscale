export const isCostOverLimit = ({ limit, cost }) => limit > 0 && limit < cost;

export const isForecastOverLimit = ({ limit, forecast }) => limit > 0 && limit < forecast;

export const getRemain = (pool) => pool.limit - pool.cost;

export const getHasLimit = (pool) => pool.limit !== 0;

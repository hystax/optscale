import { getPercentageChange } from "./math";

export const isExpensesCloseToLimit = (value, pool) => value !== 0 && getPercentageChange(value, pool) < 10;

export const TOTAL_EXPENSE_LIMIT = "total_expense_limit";
export const DAILY_EXPENSE_LIMIT = "daily_expense_limit";
export const TTL = "ttl";

export const CONSTRAINTS = [TTL, TOTAL_EXPENSE_LIMIT, DAILY_EXPENSE_LIMIT];

export const CONSTRAINTS_TYPES = Object.freeze({
  [TOTAL_EXPENSE_LIMIT]: "totalExpenseLimit",
  [DAILY_EXPENSE_LIMIT]: "dailyExpenseLimit",
  [TTL]: "ttl"
});

export const CONSTRAINT_MESSAGE_FORMAT = Object.freeze({
  TEXT: "text",
  DATETIME: "datetime",
  EXPIRES_AT_DATETIME: "expiresAtDatetime"
});

export const isExpensesLimit = (limitType) => [TOTAL_EXPENSE_LIMIT, DAILY_EXPENSE_LIMIT].includes(limitType);

export const isTtlLimit = (limitType) => limitType === TTL;

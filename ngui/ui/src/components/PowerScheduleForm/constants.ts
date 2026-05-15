import { generateDayHours } from "utils/datetime";

export const FIELD_NAMES = Object.freeze({
  NAME: "name",
  TIME_ZONE: "timeZone",
  INITIATION_DATE: "initiationDate",
  EXPIRATION_DATE: "expirationDate",
  TRIGGERS_FIELD_ARRAY: Object.freeze({
    FIELD_NAME: "triggers",
    TIME: "time",
    MERIDIEM: "meridiem",
    ACTION: "action",
    DAYS_OF_WEEK: "daysOfWeek",
  }),
});

export const TIME_VALUES = generateDayHours({ stepMinutes: 15 });

// 0=Monday ... 6=Sunday (matches Python datetime.weekday())
export const DAY_OF_WEEK_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

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
  }),
});

export const TIME_VALUES = generateDayHours({ stepMinutes: 15 });

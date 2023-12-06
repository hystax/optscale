import { generateDayHours } from "utils/datetime";

export const FIELD_NAMES = Object.freeze({
  NAME: "name",
  POWER_ON: {
    FIELD: "powerOn",
    TIME: "time",
    TIME_OF_DAY: "timeOfDay"
  },
  POWER_OFF: {
    FIELD: "powerOff",
    TIME: "time",
    TIME_OF_DAY: "timeOfDay"
  },
  TIME_ZONE: "timeZone",
  INITIATION_DATE: "initiationDate",
  EXPIRATION_DATE: "expirationDate"
});

export const TIME_VALUES = generateDayHours({ stepMinutes: 15 });

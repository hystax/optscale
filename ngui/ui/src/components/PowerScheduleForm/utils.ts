import { PowerScheduleApiParams } from "services/PowerScheduleService";
import {
  EN_TIME_FORMAT,
  EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM,
  endOfDay,
  formatTimeString,
  millisecondsToSeconds,
  moveDateFromUTC,
  parse,
  startOfDay,
} from "utils/datetime";
import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getNameApiParam = (formData: FormValues): PowerScheduleApiParams["name"] => formData[FIELD_NAMES.NAME];

export const getTimeZoneApiParam = (formData: FormValues): PowerScheduleApiParams["timezone"] =>
  formData[FIELD_NAMES.TIME_ZONE];

export const getStartDateApiParam = (formData: FormValues): PowerScheduleApiParams["start_date"] =>
  formData[FIELD_NAMES.INITIATION_DATE]
    ? millisecondsToSeconds(moveDateFromUTC(startOfDay(formData[FIELD_NAMES.INITIATION_DATE] as Date)))
    : undefined;

export const getEndDateApiParam = (formData: FormValues): PowerScheduleApiParams["end_date"] =>
  formData[FIELD_NAMES.EXPIRATION_DATE]
    ? millisecondsToSeconds(moveDateFromUTC(endOfDay(formData[FIELD_NAMES.EXPIRATION_DATE] as Date)))
    : undefined;

export const getTriggersApiParam = (formData: FormValues): PowerScheduleApiParams["triggers"] =>
  formData[FIELD_NAMES.TRIGGERS_FIELD_ARRAY.FIELD_NAME]
    .map((trigger) => {
      const formTime = trigger[FIELD_NAMES.TRIGGERS_FIELD_ARRAY.TIME];
      const meridiem = trigger[FIELD_NAMES.TRIGGERS_FIELD_ARRAY.MERIDIEM];

      return {
        time: formatTimeString({
          timeString: `${formTime} ${meridiem}`,
          timeStringFormat: EN_TIME_FORMAT,
          parsedTimeStringFormat: EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM,
        }),
        action: trigger.action,
      };
    })
    .sort((a, b) => {
      const timeA = parse(a.time, EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM, new Date());
      const timeB = parse(b.time, EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM, new Date());

      return timeA.getTime() - timeB.getTime();
    });

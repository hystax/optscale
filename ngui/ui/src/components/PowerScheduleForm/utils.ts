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
import { FormValues, TagEntry } from "./types";

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

export const getTagSelectorApiParam = (formData: FormValues): PowerScheduleApiParams["tag_selector"] => {
  const { tagSelector } = formData;
  if (!tagSelector?.enabled) return undefined;
  const validTags = (tagSelector.tags ?? []).filter((t: TagEntry) => t.key.trim() && t.value.trim());
  if (!validTags.length) return undefined;
  const resourceTypes = [...(tagSelector.includeEc2 ? ["Instance"] : []), ...(tagSelector.includeRds ? ["RDS Instance"] : [])];
  if (!resourceTypes.length) return undefined;
  return {
    tags: Object.fromEntries(validTags.map(({ key, value }: TagEntry) => [key.trim(), value.trim()])),
    resource_types: resourceTypes,
  };
};

export const getTriggersApiParam = (formData: FormValues): PowerScheduleApiParams["triggers"] =>
  formData[FIELD_NAMES.TRIGGERS_FIELD_ARRAY.FIELD_NAME]
    .map((trigger) => {
      const formTime = trigger[FIELD_NAMES.TRIGGERS_FIELD_ARRAY.TIME];
      const meridiem = trigger[FIELD_NAMES.TRIGGERS_FIELD_ARRAY.MERIDIEM];
      const daysOfWeek = trigger[FIELD_NAMES.TRIGGERS_FIELD_ARRAY.DAYS_OF_WEEK];

      return {
        time: formatTimeString({
          timeString: `${formTime} ${meridiem}`,
          timeStringFormat: EN_TIME_FORMAT,
          parsedTimeStringFormat: EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM,
        }),
        action: trigger.action,
        ...(daysOfWeek?.length ? { days_of_week: daysOfWeek } : {}),
      };
    })
    .sort((a, b) => {
      const timeA = parse(a.time, EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM, new Date());
      const timeB = parse(b.time, EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM, new Date());

      return timeA.getTime() - timeB.getTime();
    });

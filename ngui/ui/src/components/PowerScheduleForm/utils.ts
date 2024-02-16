import { PowerScheduleApiParams } from "services/PowerScheduleService";
import {
  EN_TIME_FORMAT,
  EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM,
  endOfDay,
  formatTimeString,
  millisecondsToSeconds,
  moveDateFromUTC,
  startOfDay
} from "utils/datetime";
import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getNameApiParam = (formData: FormValues): PowerScheduleApiParams["name"] => formData[FIELD_NAMES.NAME];

export const getPowerOnApiParam = (formData: FormValues): PowerScheduleApiParams["power_on"] =>
  formatTimeString({
    timeString: `${formData[FIELD_NAMES.POWER_ON.FIELD][FIELD_NAMES.POWER_ON.TIME]} ${
      formData[FIELD_NAMES.POWER_ON.FIELD][FIELD_NAMES.POWER_ON.TIME_OF_DAY]
    }`,
    timeStringFormat: EN_TIME_FORMAT,
    parsedTimeStringFormat: EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM
  });

export const getPowerOffApiParam = (formData: FormValues): PowerScheduleApiParams["power_off"] =>
  formatTimeString({
    timeString: `${formData[FIELD_NAMES.POWER_OFF.FIELD][FIELD_NAMES.POWER_OFF.TIME]} ${
      formData[FIELD_NAMES.POWER_OFF.FIELD][FIELD_NAMES.POWER_OFF.TIME_OF_DAY]
    }`,
    timeStringFormat: EN_TIME_FORMAT,
    parsedTimeStringFormat: EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM
  });

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

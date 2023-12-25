import { millisecondsToSeconds, moveDateFromUTC, secondsToMilliseconds } from "utils/datetime";
import { FIELD_NAMES } from "./constants";

export const getDefaultValues = (dataset) => ({
  [FIELD_NAMES.PATH]: dataset?.path ?? "",
  [FIELD_NAMES.NAME]: dataset?.name ?? "",
  [FIELD_NAMES.TRAINING_SET_ID]: dataset?.training_set?.path ?? "",
  [FIELD_NAMES.TRAINING_SET_TIMESPAN_FROM]: dataset?.training_set?.timespan_from
    ? secondsToMilliseconds(dataset.training_set.timespan_from)
    : undefined,
  [FIELD_NAMES.TRAINING_SET_TIMESPAN_TO]: dataset?.training_set?.timespan_to
    ? secondsToMilliseconds(dataset.training_set.timespan_to)
    : undefined,
  [FIELD_NAMES.VALIDATION_SET_ID]: dataset?.validation_set?.path ?? "",
  [FIELD_NAMES.VALIDATION_SET_TIMESPAN_FROM]: dataset?.validation_set?.timespan_from
    ? secondsToMilliseconds(dataset.validation_set.timespan_from)
    : undefined,
  [FIELD_NAMES.VALIDATION_SET_TIMESPAN_TO]: dataset?.validation_set?.timespan_to
    ? secondsToMilliseconds(dataset.validation_set.timespan_to)
    : undefined,
  [FIELD_NAMES.DESCRIPTION]: dataset?.description ?? "",
  [FIELD_NAMES.LABELS]: dataset?.labels ?? []
});

export const prepareFormSubmissionData = (formData) => ({
  description: formData[FIELD_NAMES.DESCRIPTION],
  labels: formData[FIELD_NAMES.LABELS],
  name: formData[FIELD_NAMES.NAME],
  path: formData[FIELD_NAMES.PATH],
  training_set: formData[FIELD_NAMES.TRAINING_SET_ID]
    ? {
        path: formData[FIELD_NAMES.TRAINING_SET_ID],
        timespan_from: formData[FIELD_NAMES.TRAINING_SET_TIMESPAN_FROM]
          ? millisecondsToSeconds(moveDateFromUTC(formData[FIELD_NAMES.TRAINING_SET_TIMESPAN_FROM]))
          : undefined,
        timespan_to: formData[FIELD_NAMES.TRAINING_SET_TIMESPAN_TO]
          ? millisecondsToSeconds(moveDateFromUTC(formData[FIELD_NAMES.TRAINING_SET_TIMESPAN_TO]))
          : undefined
      }
    : null,
  validation_set: formData[FIELD_NAMES.VALIDATION_SET_ID]
    ? {
        path: formData[FIELD_NAMES.VALIDATION_SET_ID],
        timespan_from: formData[FIELD_NAMES.VALIDATION_SET_TIMESPAN_FROM]
          ? millisecondsToSeconds(moveDateFromUTC(formData[FIELD_NAMES.VALIDATION_SET_TIMESPAN_FROM]))
          : undefined,
        timespan_to: formData[FIELD_NAMES.VALIDATION_SET_TIMESPAN_TO]
          ? millisecondsToSeconds(moveDateFromUTC(formData[FIELD_NAMES.VALIDATION_SET_TIMESPAN_TO]))
          : undefined
      }
    : null
});

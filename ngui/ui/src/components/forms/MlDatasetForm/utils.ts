import { millisecondsToSeconds, secondsToMilliseconds } from "utils/datetime";
import { FIELD_NAMES } from "./constants";
import { FormSubmitValues, FormValues } from "./types";

export const getDefaultValues = (dataset): FormValues => ({
  [FIELD_NAMES.PATH]: dataset?.path ?? "",
  [FIELD_NAMES.NAME]: dataset?.name ?? "",
  [FIELD_NAMES.TIMESPAN_FROM]: dataset?.timespan_from ? secondsToMilliseconds(dataset.timespan_from) : undefined,
  [FIELD_NAMES.TIMESPAN_TO]: dataset?.timespan_to ? secondsToMilliseconds(dataset.timespan_to) : undefined,
  [FIELD_NAMES.DESCRIPTION]: dataset?.description ?? "",
  [FIELD_NAMES.LABELS]: dataset?.labels ?? []
});

export const prepareFormSubmissionData = (formData: FormValues): FormSubmitValues => ({
  description: formData[FIELD_NAMES.DESCRIPTION],
  labels: formData[FIELD_NAMES.LABELS],
  name: formData[FIELD_NAMES.NAME],
  path: formData[FIELD_NAMES.PATH],
  timespan_from: formData[FIELD_NAMES.TIMESPAN_FROM] ? millisecondsToSeconds(formData[FIELD_NAMES.TIMESPAN_FROM]) : null,
  timespan_to: formData[FIELD_NAMES.TIMESPAN_TO] ? millisecondsToSeconds(formData[FIELD_NAMES.TIMESPAN_TO]) : null
});

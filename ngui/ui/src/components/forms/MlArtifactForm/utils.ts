import { FIELD_NAMES } from "./constants";
import { Artifact, FormSubmitValues, FormValues } from "./types";

export const getDefaultValues = (artifact: Artifact = {}): FormValues => ({
  [FIELD_NAMES.PATH]: artifact?.path ?? "",
  [FIELD_NAMES.NAME]: artifact?.name ?? "",
  [FIELD_NAMES.DESCRIPTION]: artifact?.description ?? "",
  [FIELD_NAMES.TAGS_FIELD_ARRAY.FIELD_NAME]: artifact?.tags
    ? Object.entries(artifact?.tags).map(([key, value]) => ({
        [FIELD_NAMES.TAGS_FIELD_ARRAY.KEY]: key,
        [FIELD_NAMES.TAGS_FIELD_ARRAY.VALUE]: value
      }))
    : [
        {
          [FIELD_NAMES.TAGS_FIELD_ARRAY.KEY]: "",
          [FIELD_NAMES.TAGS_FIELD_ARRAY.VALUE]: ""
        }
      ]
});

export const prepareFormSubmissionData = (formData: FormValues): FormSubmitValues => ({
  name: formData[FIELD_NAMES.NAME],
  path: formData[FIELD_NAMES.PATH],
  description: formData[FIELD_NAMES.DESCRIPTION],
  tags: Object.fromEntries(
    formData[FIELD_NAMES.TAGS_FIELD_ARRAY.FIELD_NAME].map(
      ({ [FIELD_NAMES.TAGS_FIELD_ARRAY.KEY]: key, [FIELD_NAMES.TAGS_FIELD_ARRAY.VALUE]: value }) => [key, value]
    )
  )
});

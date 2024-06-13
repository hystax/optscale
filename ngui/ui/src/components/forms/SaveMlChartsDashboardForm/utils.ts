import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getDefaultValues = ({ name, saveAs, share }: { name: string; saveAs: string; share: boolean }): FormValues => ({
  [FIELD_NAMES.NAME]: name,
  [FIELD_NAMES.SAVE_AS]: saveAs,
  [FIELD_NAMES.SHARE]: share
});

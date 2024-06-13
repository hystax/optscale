import { sortObjectsAlphabetically } from "utils/arrays";
import { FIELD_NAMES } from "./constants";
import { FormValues, Owner } from "./types";

export const getDefaultValues = ({ bookSince }: { bookSince?: number }): FormValues => ({
  [FIELD_NAMES.BOOKING_OWNER]: "",
  [FIELD_NAMES.BOOK_SINCE]: bookSince,
  [FIELD_NAMES.BOOK_UNTIL]: undefined
});

export const sortOwnersAlphabeticallyByName = (owners: Owner[]) => sortObjectsAlphabetically({ array: owners, field: "name" });

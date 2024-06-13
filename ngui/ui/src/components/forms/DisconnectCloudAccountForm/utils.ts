import { FIELD_NAMES, REASONS } from "./constants";
import { Reason } from "./types";

export const getReasonValue = (reason: Reason) =>
  (
    ({
      [REASONS.SAVINGS]: "The product does not give enough cost savings",
      [REASONS.FEATURES]: "OptScale does not work as expected / not enough features",
      [REASONS.GOAL]: "I have achieved my goal and am not interested in it anymore",
      [REASONS.OTHER]: "Other"
    }) as const
  )[reason];

export const getDefaultValues = () =>
  ({
    [FIELD_NAMES.REASON]: "",
    [FIELD_NAMES.OTHER_REASON]: "",
    [FIELD_NAMES.MISSING_CAPABILITIES]: ""
  }) as const;

import React from "react";
import { select } from "@storybook/addon-knobs";
import ContentBackdrop, { MESSAGE_TYPES } from "components/ContentBackdrop";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/ContentBackdrop`
};

export const withKnobs = () => (
  <ContentBackdrop
    messageType={select(
      "messageType",
      [
        MESSAGE_TYPES.ASSIGNMENT_RULES,
        MESSAGE_TYPES.CLOUD_ACCOUNTS,
        MESSAGE_TYPES.RECOMMENDATIONS,
        MESSAGE_TYPES.POOLS,
        MESSAGE_TYPES.ENVIRONMENTS
      ],
      MESSAGE_TYPES.CLOUD_ACCOUNTS
    )}
  />
);

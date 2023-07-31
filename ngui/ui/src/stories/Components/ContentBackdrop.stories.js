import React from "react";
import ContentBackdrop, { MESSAGE_TYPES } from "components/ContentBackdrop";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/ContentBackdrop`,
  argTypes: {
    messageType: {
      name: "Message type",
      control: "select",
      options: [
        MESSAGE_TYPES.ASSIGNMENT_RULES,
        MESSAGE_TYPES.CLOUD_ACCOUNTS,
        MESSAGE_TYPES.RECOMMENDATIONS,
        MESSAGE_TYPES.POOLS,
        MESSAGE_TYPES.ENVIRONMENTS
      ],
      defaultValue: MESSAGE_TYPES.CLOUD_ACCOUNTS
    }
  }
};

export const withKnobs = (args) => <ContentBackdrop messageType={args.messageType} bannerContent={<div>Banner content</div>} />;

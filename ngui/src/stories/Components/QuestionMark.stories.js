import React from "react";
import { text, select, boolean } from "@storybook/addon-knobs";
import QuestionMark from "components/QuestionMark";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/QuestionMark`
};

export const basic = () => <QuestionMark messageId="assignmentRuleConditionsDescription" />;

const fontSizeOptions = {
  inherit: "inherit",
  default: "default",
  small: "small",
  large: "large"
};

export const withKnobs = () => (
  <QuestionMark
    messageId={text("messageId", "assignmentRuleConditionsDescription")}
    fontSize={select("fontSize", fontSizeOptions, "default")}
    rightSide={boolean("rightSide", false)}
  />
);

import React from "react";
import { text, select } from "@storybook/addon-knobs";
import KeyValueLabel from "components/KeyValueLabel";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/KeyValueLabel`
};

export const basic = () => <KeyValueLabel messageId="name" value="value" />;

export const withKnobs = () => (
  <KeyValueLabel
    messageId={text("messageId", "name")}
    text={text("text", "")}
    value={text("value", "value")}
    separator={select("separator", ["colon", "hyphen"], "colon")}
  />
);

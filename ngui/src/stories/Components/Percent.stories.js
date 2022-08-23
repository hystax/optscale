import React from "react";
import { number } from "@storybook/addon-knobs";
import Percent from "components/Percent";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Percent`
};

export const basic = () => <Percent value={5} />;

export const withKnobs = () => <Percent value={number("value", 4.2)} minimumFractionDigits={2} />;

import React from "react";
import { number } from "@storybook/addon-knobs";
import TabsLoader from "components/TabsLoader";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/TabsLoader`
};

export const withKnobs = () => <TabsLoader tabsCount={number("Number of tabs", 1)} />;

import React from "react";
import TabsLoader from "components/TabsLoader";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/TabsLoader`,
  argTypes: {
    tabCount: { name: "Tab count", control: "number", defaultValue: 1 }
  }
};

export const withKnobs = (args) => <TabsLoader tabsCount={args.tabCount} />;

import TabsLoader from "components/TabsLoader";

export default {
  component: TabsLoader,
  argTypes: {
    tabCount: { name: "Tab count", control: "number", defaultValue: 1 }
  }
};

export const withKnobs = (args) => <TabsLoader tabsCount={args.tabCount} />;

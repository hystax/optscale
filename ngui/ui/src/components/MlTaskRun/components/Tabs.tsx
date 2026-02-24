import { useState } from "react";
import TabsWrapper from "components/TabsWrapper";

export const TABS = Object.freeze({
  OVERVIEW: "overview",
  ARTIFACTS: "artifacts",
  CHARTS: "charts",
  EXECUTORS: "executors",
});

const Tabs = ({ overviewTab, chartsTab, artifactsTab, executorsTab }) => {
  const [activeTab, setActiveTab] = useState();

  const tabs = [
    {
      title: TABS.OVERVIEW,
      dataTestId: "tab_overview",
      node: overviewTab,
    },
    {
      title: TABS.CHARTS,
      dataTestId: "tab_charts",
      node: chartsTab,
    },
    {
      title: TABS.ARTIFACTS,
      dataTestId: "tab_artifact",
      node: artifactsTab,
    },
    {
      title: TABS.EXECUTORS,
      dataTestId: "tab_executors",
      node: executorsTab,
    },
  ];

  return (
    <TabsWrapper
      tabsProps={{
        tabs,
        defaultTab: TABS.OVERVIEW,
        name: "ml-task-run-details",
        activeTab,
        handleChange: (event, value) => {
          setActiveTab(value);
        },
      }}
    />
  );
};

export default Tabs;

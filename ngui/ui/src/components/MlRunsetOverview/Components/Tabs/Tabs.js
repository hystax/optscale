import React, { useState } from "react";
import PropTypes from "prop-types";
import TabsWrapper from "components/TabsWrapper";
import MlRunsetExecutorsContainer from "containers/MlRunsetExecutorsContainer";
import Runs from "./Runs";

const TABS = Object.freeze({
  RUNS: "runs",
  RUNNERS: "executors"
});

const Tabs = ({ runs, isGetRunsetRunsLoading }) => {
  const [activeTab, setActiveTab] = useState();

  const tabs = [
    {
      title: TABS.RUNS,
      dataTestId: "tab_runs",
      node: <Runs isLoading={isGetRunsetRunsLoading} runs={runs} />
    },
    {
      title: TABS.RUNNERS,
      dataTestId: "tab_executors",
      node: <MlRunsetExecutorsContainer />
    }
  ];

  return (
    <TabsWrapper
      tabsProps={{
        tabs,
        defaultTab: TABS.RUNS,
        name: "ml-runs",
        activeTab,
        handleChange: (event, value) => {
          setActiveTab(value);
        }
      }}
    />
  );
};

Tabs.propTypes = {
  runs: PropTypes.array.isRequired,
  isGetRunsetRunsLoading: PropTypes.bool
};

export default Tabs;

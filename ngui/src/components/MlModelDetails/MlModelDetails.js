import React, { useState } from "react";
import PropTypes from "prop-types";
import PageContentWrapper from "components/PageContentWrapper";
import TabsWrapper from "components/TabsWrapper";
import MlModelExecutorsContainer from "containers/MlModelExecutorsContainer";
import MlModelRunsListContainer from "containers/MlModelRunsListContainer";
import { ML_MODEL_DETAILS_TABS } from "utils/constants";
import ModelActionBar from "./ModelActionBar";
import ModelDetailsSummary from "./ModelDetailsSummary";

const Tabs = ({ application, isLoading = false }) => {
  const [activeTab, setActiveTab] = useState();

  const tabs = [
    {
      title: ML_MODEL_DETAILS_TABS.OVERVIEW,
      dataTestId: "tab_overview",
      node: (
        <ModelDetailsSummary application={application} isLoading={isLoading} onTabChange={(tabName) => setActiveTab(tabName)} />
      )
    },
    {
      title: ML_MODEL_DETAILS_TABS.RUNS,
      dataTestId: "tab_runs",
      node: <MlModelRunsListContainer />
    },
    {
      title: ML_MODEL_DETAILS_TABS.EXECUTORS,
      dataTestId: "tab_executors",
      node: <MlModelExecutorsContainer applicationId={application.id} />
    }
  ];

  return (
    <TabsWrapper
      tabsProps={{
        tabs,
        defaultTab: ML_MODEL_DETAILS_TABS.OVERVIEW,
        name: "ml-model-run-details",
        activeTab,
        handleChange: (event, value) => {
          setActiveTab(value);
        }
      }}
    />
  );
};

const MlModelDetails = ({ application = {}, isLoading }) => (
  <>
    <ModelActionBar name={application.name} applicationId={application.id} isLoading={isLoading} />
    <PageContentWrapper>
      <Tabs application={application} isLoading={isLoading} />
    </PageContentWrapper>
  </>
);

MlModelDetails.propTypes = {
  isLoading: PropTypes.bool,
  application: PropTypes.object
};

export default MlModelDetails;

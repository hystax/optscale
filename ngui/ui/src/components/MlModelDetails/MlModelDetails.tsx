import { useState } from "react";
import PageContentWrapper from "components/PageContentWrapper";
import TabsWrapper from "components/TabsWrapper";
import MlModelExecutorsContainer from "containers/MlModelExecutorsContainer";
import MlModelRecommendationsContainer from "containers/MlModelRecommendationsContainer";
import { ML_MODEL_DETAILS_TABS } from "utils/constants";
import ModelActionBar from "./ModelActionBar";

const Tabs = ({ model, isLoading = false }) => {
  const [activeTab, setActiveTab] = useState();

  const tabs = [
    {
      title: ML_MODEL_DETAILS_TABS.OVERVIEW,
      dataTestId: "tab_overview",
      node: <MlModelRecommendationsContainer model={model} isModelDetailsLoading={isLoading} />
    },
    {
      title: ML_MODEL_DETAILS_TABS.EXECUTORS,
      dataTestId: "tab_executors",
      node: <MlModelExecutorsContainer />
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

const MlModelDetails = ({ model = {}, isLoading }) => (
  <>
    <ModelActionBar name={model.name} modelKey={model.key} modelId={model.id} isLoading={isLoading} />
    <PageContentWrapper>
      <Tabs model={model} isLoading={isLoading} />
    </PageContentWrapper>
  </>
);

export default MlModelDetails;

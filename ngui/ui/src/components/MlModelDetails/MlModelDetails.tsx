import { useState } from "react";
import { Stack } from "@mui/material";
import PageContentWrapper from "components/PageContentWrapper";
import TabsWrapper from "components/TabsWrapper";
import MlModelExecutorsContainer from "containers/MlModelExecutorsContainer";
import MlModelLeaderboardContainer from "containers/MlModelLeaderboardContainer";
import MlModelRecommendationsContainer from "containers/MlModelRecommendationsContainer";
import MlModelRunsListContainer from "containers/MlModelRunsListContainer";
import MlModelSummaryCardsContainer from "containers/MlModelSummaryCardsContainer";
import { ML_MODEL_DETAILS_TABS, ML_MODEL_DETAILS_TAB_NAME } from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import ModelActionBar from "./ModelActionBar";
import ModelDetailsSummary from "./ModelDetailsSummary";

const Tabs = ({ model, isLoading = false }) => {
  const [activeTab, setActiveTab] = useState();

  const tabs = [
    {
      title: ML_MODEL_DETAILS_TABS.OVERVIEW,
      dataTestId: "tab_overview",
      node: <ModelDetailsSummary model={model} isModelDetailsLoading={isLoading} />
    },
    {
      title: ML_MODEL_DETAILS_TABS.RUNS,
      dataTestId: "tab_runs",
      node: <MlModelRunsListContainer />
    },
    {
      title: ML_MODEL_DETAILS_TABS.LEADERBOARDS,
      dataTestId: "tab_leaderboards",
      node: <MlModelLeaderboardContainer />
    },
    {
      title: ML_MODEL_DETAILS_TABS.RECOMMENDATIONS,
      dataTestId: "tab_recommendations",
      node: <MlModelRecommendationsContainer />
    },
    {
      title: ML_MODEL_DETAILS_TABS.EXECUTORS,
      dataTestId: "tab_executors",
      node: <MlModelExecutorsContainer />
    }
  ];

  return (
    <Stack spacing={SPACING_2}>
      <div>
        <MlModelSummaryCardsContainer model={model} isModelDetailsLoading={isLoading} />
      </div>
      <div>
        <TabsWrapper
          tabsProps={{
            tabs,
            queryTabName: ML_MODEL_DETAILS_TAB_NAME,
            defaultTab: ML_MODEL_DETAILS_TABS.OVERVIEW,
            name: "ml-model-run-details",
            activeTab,
            handleChange: (event, value) => {
              setActiveTab(value);
            }
          }}
        />
      </div>
    </Stack>
  );
};

const MlModelDetails = ({ model = {}, isLoading, isDataReady = true }) => (
  <>
    <ModelActionBar name={model.name} isDataReady={isDataReady} taskKey={model.key} taskId={model.id} isLoading={isLoading} />
    <PageContentWrapper>
      <Tabs model={model} isLoading={isLoading} />
    </PageContentWrapper>
  </>
);

export default MlModelDetails;

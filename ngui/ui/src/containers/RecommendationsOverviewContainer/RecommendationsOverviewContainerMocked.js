import React from "react";
import { ALL_SERVICES } from "hooks/useRecommendationServices";
import { DEFAULT_RECOMMENDATIONS_FILTER, DEFAULT_VIEW } from "./Filters";
import { MOCKED_DATA } from "./mockedData";
import { ALL_RECOMMENDATIONS } from "./recommendations/allRecommendations";
import { ACTIVE } from "./recommendations/BaseRecommendation";
import RecommendationsOverview from "./RecommendationsOverview";

const fn = () => {};
const RecommendationsOverviewContainerMocked = () => {
  const recommendations = Object.values(ALL_RECOMMENDATIONS).map(
    (RecommendationClass) => new RecommendationClass(ACTIVE, MOCKED_DATA)
  );

  return (
    <RecommendationsOverview
      data={MOCKED_DATA}
      isDataReady
      onRecommendationClick={fn}
      setCategory={fn}
      category={DEFAULT_RECOMMENDATIONS_FILTER}
      setSearch={fn}
      search=""
      setView={fn}
      view={DEFAULT_VIEW}
      setService={fn}
      service={ALL_SERVICES}
      recommendations={recommendations}
      downloadLimit={0}
      riSpExpensesSummary={{
        totalCostWithOffer: 208.83945818440003,
        totalSaving: 44.93673360120001,
        computeExpensesCoveredWithCommitments: 0.07
      }}
      isRiSpExpensesSummaryLoading={false}
    />
  );
};

RecommendationsOverviewContainerMocked.propTypes = {};

export default RecommendationsOverviewContainerMocked;

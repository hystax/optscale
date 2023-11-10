import { PageMockupContextProvider } from "contexts/PageMockupContext";
import { useAllRecommendations } from "hooks/useAllRecommendations";
import { ALL_SERVICES } from "hooks/useRecommendationServices";
import { DEFAULT_RECOMMENDATIONS_FILTER, DEFAULT_VIEW } from "./Filters";
import { MOCKED_DATA } from "./mockedData";
import RecommendationsOverview from "./RecommendationsOverview";

const fn = () => {};

const RecommendationsOverviewContainerMocked = () => {
  const allRecommendations = useAllRecommendations();

  return (
    <PageMockupContextProvider>
      <RecommendationsOverview
        lastCompleted={MOCKED_DATA.last_completed}
        totalSaving={MOCKED_DATA.total_saving}
        nextRun={MOCKED_DATA.next_run}
        lastRun={MOCKED_DATA.last_run}
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
        recommendationsData={MOCKED_DATA}
        recommendationClasses={allRecommendations}
        downloadLimit={0}
        riSpExpensesSummary={{
          totalCostWithOffer: 208.83945818440003,
          totalSaving: 44.93673360120001,
          computeExpensesCoveredWithCommitments: 0.07
        }}
        isRiSpExpensesSummaryLoading={false}
      />
    </PageMockupContextProvider>
  );
};

export default RecommendationsOverviewContainerMocked;

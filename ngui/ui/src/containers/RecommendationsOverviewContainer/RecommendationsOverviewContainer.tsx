import { useCallback } from "react";
import { RecommendationModal } from "components/SideModalManager/SideModals";
import { useGetIsRecommendationsDownloadAvailable } from "hooks/useGetIsRecommendationsDownloadAvailable";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOptscaleRecommendations } from "hooks/useOptscaleRecommendations";
import { ALL_SERVICES, useRecommendationServices } from "hooks/useRecommendationServices";
import { useRiSpExpensesSummary } from "hooks/useRiSpExpensesSummary";
import { useSyncQueryParamWithState } from "hooks/useSyncQueryParamWithState";
import OrganizationOptionsService from "services/OrganizationOptionsService";
import RecommendationsOverviewService from "services/RecommendationsOverviewService";
import {
  RECOMMENDATION_CATEGORY_QUERY_PARAMETER,
  RECOMMENDATION_SERVICE_QUERY_PARAMETER,
  RECOMMENDATION_VIEW_QUERY_PARAMETER
} from "urls";
import { RECOMMENDATIONS_LIMIT_FILTER } from "utils/constants";
import { DEFAULT_RECOMMENDATIONS_FILTER, DEFAULT_VIEW, POSSIBLE_RECOMMENDATIONS_FILTERS, POSSIBLE_VIEWS } from "./Filters";
import RecommendationsOverview from "./RecommendationsOverview";
import {
  setCategory as setCategoryActionCreator,
  setService as setServiceActionCreator,
  setView as setViewActionCreator
} from "./redux/controlsState/actionCreators";
import { useControlState } from "./redux/controlsState/hooks";
import { VALUE_ACCESSORS } from "./redux/controlsState/reducer";

const OPTION_PREFIX = "recommendation_";

type RecommendationsOverviewContainerProps = {
  selectedDataSourceIds: string[];
  selectedDataSourceTypes: string[];
};

const RecommendationsOverviewContainer = ({
  selectedDataSourceIds,
  selectedDataSourceTypes
}: RecommendationsOverviewContainerProps) => {
  const { useGet, useGetRecommendationsDownloadOptions } = OrganizationOptionsService();
  const { options: downloadOptions } = useGetRecommendationsDownloadOptions();
  const { options } = useGet(true);
  const downloadLimit = downloadOptions?.limit ?? RECOMMENDATIONS_LIMIT_FILTER;

  const services = useRecommendationServices();

  const [category, setCategory] = useControlState({
    redux: { stateAccessor: VALUE_ACCESSORS.CATEGORY, actionCreator: setCategoryActionCreator },
    queryParamName: RECOMMENDATION_CATEGORY_QUERY_PARAMETER,
    defaultValue: DEFAULT_RECOMMENDATIONS_FILTER,
    possibleStates: POSSIBLE_RECOMMENDATIONS_FILTERS
  });

  const [service, setService] = useControlState({
    redux: { stateAccessor: VALUE_ACCESSORS.SERVICE, actionCreator: setServiceActionCreator },
    queryParamName: RECOMMENDATION_SERVICE_QUERY_PARAMETER,
    defaultValue: ALL_SERVICES,
    possibleStates: Object.keys(services)
  });

  const [view, setView] = useControlState({
    redux: { stateAccessor: VALUE_ACCESSORS.VIEW, actionCreator: setViewActionCreator },
    queryParamName: RECOMMENDATION_VIEW_QUERY_PARAMETER,
    defaultValue: DEFAULT_VIEW,
    possibleStates: POSSIBLE_VIEWS
  });

  const [search, setSearch] = useSyncQueryParamWithState({
    queryParamName: "search",
    defaultValue: ""
  });

  const { useGetOptimizationsOverview } = RecommendationsOverviewService();

  const { data, isDataReady } = useGetOptimizationsOverview(selectedDataSourceIds);

  const optscaleRecommendations = useOptscaleRecommendations();

  const organizationRecommendationOptions = options
    .filter(({ name }) =>
      /**
       * The options API has 2 output formats: an array of names ([string]) and an array of objects ([{name, value}]).
       * On the "Org options" page, we request options with withValues set to false, giving us an array of strings.
       * However, on the Recommendations page, when trying to access the "name" property, it's undefined, resulting in a "cannot read property" error.
       * Adding `?.` fixes OS-6409
       */
      name?.startsWith(OPTION_PREFIX)
    )
    .reduce((result, { name, value }) => ({ ...result, [name.slice(OPTION_PREFIX.length)]: value }), {});

  const openSideModal = useOpenSideModal();

  const onRecommendationClick = useCallback(
    (recommendation) => {
      openSideModal(RecommendationModal, {
        type: recommendation.type,
        titleMessageId: recommendation.title,
        limit: downloadLimit,
        dataSourceIds: selectedDataSourceIds,
        dismissable: recommendation.dismissable,
        withExclusions: recommendation.withExclusions
      });
    },
    [downloadLimit, openSideModal, selectedDataSourceIds]
  );

  const { isLoading: isRiSpExpensesSummaryLoading, summary: riSpExpensesSummary } =
    useRiSpExpensesSummary(selectedDataSourceIds);

  const { isLoading: isGetIsDownloadAvailableLoading, isDownloadAvailable } = useGetIsRecommendationsDownloadAvailable();

  return (
    <RecommendationsOverview
      lastCompleted={data.last_completed}
      totalSaving={data.total_saving}
      nextRun={data.next_run}
      lastRun={data.last_run}
      isDataReady={isDataReady}
      onRecommendationClick={onRecommendationClick}
      setCategory={setCategory}
      category={category}
      setSearch={setSearch}
      search={search}
      setView={setView}
      view={view}
      setService={setService}
      service={service}
      recommendationsData={{ ...data, organizationOptions: organizationRecommendationOptions }}
      recommendationClasses={optscaleRecommendations}
      downloadLimit={downloadLimit}
      riSpExpensesSummary={riSpExpensesSummary}
      isRiSpExpensesSummaryLoading={isRiSpExpensesSummaryLoading}
      isDownloadAvailable={isDownloadAvailable}
      isGetIsDownloadAvailableLoading={isGetIsDownloadAvailableLoading}
      selectedDataSourceIds={selectedDataSourceIds}
      selectedDataSourceTypes={selectedDataSourceTypes}
    />
  );
};

export default RecommendationsOverviewContainer;

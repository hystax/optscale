import React, { useCallback } from "react";
import PropTypes from "prop-types";
import { RecommendationModal } from "components/SideModalManager/SideModals";
import { useGetIsRecommendationsDownloadAvailable } from "hooks/useGetIsRecommendationsDownloadAvailable";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { ALL_SERVICES, useRecommendationServices } from "hooks/useRecommendationServices";
import { useRiSpExpensesSummary } from "hooks/useRiSpExpensesSummary";
import { useSyncQueryParamWithState } from "hooks/useSyncQueryParamWithState";
import OrganizationOptionsService from "services/OrganizationOptionsService";
import {
  RECOMMENDATION_CATEGORY_QUERY_PARAMETER,
  RECOMMENDATION_SERVICE_QUERY_PARAMETER,
  RECOMMENDATION_VIEW_QUERY_PARAMETER
} from "urls";
import { RECOMMENDATIONS_LIMIT_FILTER } from "utils/constants";
import { DEFAULT_RECOMMENDATIONS_FILTER, DEFAULT_VIEW, POSSIBLE_RECOMMENDATIONS_FILTERS, POSSIBLE_VIEWS } from "./Filters";
import { OPTSCALE_RECOMMENDATIONS } from "./recommendations/allRecommendations";
import RecommendationsOverview from "./RecommendationsOverview";
import RecommendationsOverviewService from "./RecommendationsOverviewService";
import {
  setCategory as setCategoryActionCreator,
  setService as setServiceActionCreator,
  setView as setViewActionCreator
} from "./redux/controlsState/actionCreators";
import { useControlState } from "./redux/controlsState/hooks";
import { VALUE_ACCESSORS } from "./redux/controlsState/reducer";

const OPTION_PREFIX = "recommendation_";

const RecommendationsOverviewContainer = ({ selectedDataSources }) => {
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

  const { data, isDataReady } = useGetOptimizationsOverview(selectedDataSources);

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
        dataSourceIds: selectedDataSources
      });
    },
    [downloadLimit, openSideModal, selectedDataSources]
  );

  const { isLoading: isRiSpExpensesSummaryLoading, summary: riSpExpensesSummary } = useRiSpExpensesSummary(selectedDataSources);

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
      recommendationClasses={OPTSCALE_RECOMMENDATIONS}
      downloadLimit={downloadLimit}
      riSpExpensesSummary={riSpExpensesSummary}
      isRiSpExpensesSummaryLoading={isRiSpExpensesSummaryLoading}
      isDownloadAvailable={isDownloadAvailable}
      isGetIsDownloadAvailableLoading={isGetIsDownloadAvailableLoading}
      selectedDataSources={selectedDataSources}
    />
  );
};

RecommendationsOverviewContainer.propTypes = {
  downloadLimit: PropTypes.number.isRequired,
  selectedDataSources: PropTypes.array.isRequired,
  isDownloadAvailable: PropTypes.bool.isRequired,
  isGetIsDownloadAvailableLoading: PropTypes.bool.isRequired
};

export default RecommendationsOverviewContainer;

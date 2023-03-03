import React, { useEffect, useState, useCallback } from "react";
import { useDispatch } from "react-redux";
import {
  getOptimizations as apiActionGetOptimizations,
  RESTAPI,
  updateResourceVisibility,
  getResourceAllowedActions,
  updateOptimizations
} from "api";
import { GET_RESOURCE_ALLOWED_ACTIONS } from "api/auth/actionTypes";
import { GET_OPTIMIZATIONS, UPDATE_OPTIMIZATIONS, UPDATE_RESOURCE_VISIBILITY } from "api/restapi/actionTypes";
import { getApiUrl } from "api/utils";
import ContentBackdropLoader from "components/ContentBackdropLoader";
import Mocked, { MESSAGE_TYPES } from "components/Mocked";
import RelevantRecommendations, { RelevantRecommendationsMocked } from "components/RelevantRecommendations";
import { SUPPORTED_CATEGORIES, ALL_CATEGORY } from "components/RelevantRecommendations/constants";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useFetchAndDownload } from "hooks/useFetchAndDownload";
import { useInitialMount } from "hooks/useInitialMount";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import OrganizationOptionsService from "services/OrganizationOptionsService";
import { isError } from "utils/api";
import { isEmpty as isEmptyArray } from "utils/arrays";
import {
  MAP_RECOMMENDATION_TYPES,
  FE_TO_BE_MAP_RECOMMENDATION_TYPES,
  RECOMMENDATIONS_LIMIT_FILTER,
  RECOMMENDATIONS_TABS,
  RESOURCE_VISIBILITY_STATUSES,
  RESOURCE_VISIBILITY_ACTIONS,
  RECOMMENDATION_TYPE_QUERY_PARAMETER
} from "utils/constants";
import { getQueryParams, updateQueryParams, removeQueryParam } from "utils/network";
import { isEmpty } from "utils/objects";
import {
  getActiveRecommendationsByCategory,
  getDismissedRecommendationsByCategory,
  getExcludedRecommendationsByCategory
} from "utils/recommendationCategories";

// tabs - array of arrays  in format «[[tabName, isEmpty]]»
const getNewSelectedTab = (selectedTab, tabs) => {
  if (tabs.every(([, isCategorizedDataEmpty]) => isCategorizedDataEmpty)) {
    return tabs[0][0];
  }

  const [firstNotEmptyTabThatNotEqualToSelected] = tabs.find(
    ([tabName, isCategorizedDataEmpty]) => tabName !== selectedTab && !isCategorizedDataEmpty
  );

  return firstNotEmptyTabThatNotEqualToSelected;
};

const getStatusBySelectedTab = (selectedTab) =>
  ({
    // TODO: key is equal to value. Do we need this layer?
    [RECOMMENDATIONS_TABS.ACTIVE]: [RESOURCE_VISIBILITY_STATUSES.ACTIVE],
    [RECOMMENDATIONS_TABS.DISMISSED]: [RESOURCE_VISIBILITY_STATUSES.DISMISSED],
    [RECOMMENDATIONS_TABS.EXCLUDED]: [RESOURCE_VISIBILITY_STATUSES.EXCLUDED]
  }[selectedTab]);

const supportedRecommendationTypes = Object.keys(FE_TO_BE_MAP_RECOMMENDATION_TYPES);

const FORCE_CHECK_NEXT_RUN = 1;

const initializeExpandedState = (optimization) =>
  supportedRecommendationTypes.reduce(
    (initialExpandedState, optimizationType) => ({
      ...initialExpandedState,
      [optimizationType]: optimizationType === optimization
    }),
    {}
  );

const initializeRecommendationCategoryState = () => {
  const { category: categoryQueryParameter } = getQueryParams();
  if (SUPPORTED_CATEGORIES.includes(categoryQueryParameter)) {
    return categoryQueryParameter;
  }
  return ALL_CATEGORY;
};

const RelevantRecommendationsDataContainer = ({ downloadLimit }) => {
  const { organizationId } = useOrganizationInfo();
  const dispatch = useDispatch();
  const { isInitialMount, setIsInitialMount } = useInitialMount();

  const {
    tab = RECOMMENDATIONS_TABS.ACTIVE,
    [RECOMMENDATION_TYPE_QUERY_PARAMETER]: queryParamRecommendationType = "",
    dataSourceId: queryParamsDataSourceId = []
  } = getQueryParams();

  const [dataSourceIdsState, setDataSourceIdsState] = useState(
    Array.isArray(queryParamsDataSourceId) ? queryParamsDataSourceId : [queryParamsDataSourceId]
  );
  const [selectedTab, setSelectedTab] = useState(
    Object.values(RECOMMENDATIONS_TABS).includes(tab) ? tab : RECOMMENDATIONS_TABS.ACTIVE
  );
  const [expanded, setExpanded] = useState(initializeExpandedState(queryParamRecommendationType));

  const [recommendationCategory, setRecommendationCategory] = useState(initializeRecommendationCategoryState);

  useEffect(() => {
    updateQueryParams({
      category: recommendationCategory
    });
  }, [recommendationCategory]);

  const {
    apiData: { optimizations = {} }
  } = useApiData(GET_OPTIMIZATIONS);

  const { categorizedRecommendations = {}, categoriesSizes = {} } = optimizations;

  const { isLoading: isUpdateRecommendationsLoading } = useApiState(UPDATE_OPTIMIZATIONS);

  const { isLoading: isGetRecommendationsLoading, shouldInvoke } = useApiState(GET_OPTIMIZATIONS, {
    organizationId,
    type: MAP_RECOMMENDATION_TYPES[queryParamRecommendationType]
  });

  const { isLoading: isGetResourceAllowedActionsLoading } = useApiState(GET_RESOURCE_ALLOWED_ACTIONS);

  const [isTabWrapperReady, setIsTabWrapperReady] = useState(!shouldInvoke);

  const updateExpanded = (recommendationName) => {
    setExpanded((prevState) => ({
      ...prevState,
      ...supportedRecommendationTypes.reduce(
        (expandedState, optimizationType) => ({
          ...expandedState,
          [optimizationType]: false
        }),
        {}
      ),
      [recommendationName]: !prevState[recommendationName]
    }));
  };

  const getOptimizations = useCallback(
    ({ type, limit, status, dataSourceIds = dataSourceIdsState }) =>
      dispatch((_, getState) => {
        dispatch(
          apiActionGetOptimizations(organizationId, {
            type,
            limit,
            status,
            cloudAccountIds: dataSourceIds
          })
        )
          .then(() => {
            const updatedOptimizations = getState()?.[RESTAPI]?.[GET_OPTIMIZATIONS]?.optimizations ?? {};

            if (type) {
              let items = [];
              if (selectedTab === RECOMMENDATIONS_TABS.ACTIVE) {
                items = updatedOptimizations.optimizations[MAP_RECOMMENDATION_TYPES[type]]?.items || [];
              }
              if (selectedTab === RECOMMENDATIONS_TABS.DISMISSED) {
                items = updatedOptimizations.dismissed_optimizations[MAP_RECOMMENDATION_TYPES[type]]?.items || [];
              }
              if (selectedTab === RECOMMENDATIONS_TABS.EXCLUDED) {
                items = updatedOptimizations.excluded_optimizations[MAP_RECOMMENDATION_TYPES[type]]?.items || [];
              }
              const ids = items.map(({ resource_id: resourceId }) => resourceId).filter(Boolean);
              if (!isEmptyArray(ids)) {
                dispatch(getResourceAllowedActions(ids));
              }
            }
          })
          .then(() => setIsTabWrapperReady(true));
      }),
    [dispatch, organizationId, dataSourceIdsState, selectedTab]
  );

  useEffect(() => {
    if (isTabWrapperReady) {
      const updatedCategorizedActiveRecommendations = getActiveRecommendationsByCategory(
        categorizedRecommendations,
        recommendationCategory
      );
      const updatedCategorizedDismissedRecommendations = getDismissedRecommendationsByCategory(
        categorizedRecommendations,
        recommendationCategory
      );

      const updatedCategorizedExcludedRecommendations = getExcludedRecommendationsByCategory(
        categorizedRecommendations,
        recommendationCategory
      );

      const isUpdatedCategorizedActiveOptimizationsEmpty = isEmpty(updatedCategorizedActiveRecommendations);
      const isUpdatedCategorizedDismissedOptimizationsEmpty = isEmpty(updatedCategorizedDismissedRecommendations);
      const isUpdatedCategorizedExcludedOptimizationsEmpty = isEmpty(updatedCategorizedExcludedRecommendations);

      const handleSuccessfulUpdate = (tabName) => {
        setSelectedTab(tabName);
        updateExpanded();
        removeQueryParam(RECOMMENDATION_TYPE_QUERY_PARAMETER);
      };

      if (
        isUpdatedCategorizedActiveOptimizationsEmpty &&
        isUpdatedCategorizedDismissedOptimizationsEmpty &&
        isUpdatedCategorizedExcludedOptimizationsEmpty
      ) {
        handleSuccessfulUpdate(RECOMMENDATIONS_TABS.ACTIVE);
        return;
      }

      const tabs = [
        [RECOMMENDATIONS_TABS.ACTIVE, isUpdatedCategorizedActiveOptimizationsEmpty],
        [RECOMMENDATIONS_TABS.DISMISSED, isUpdatedCategorizedDismissedOptimizationsEmpty],
        [RECOMMENDATIONS_TABS.EXCLUDED, isUpdatedCategorizedExcludedOptimizationsEmpty]
      ];

      if (
        (selectedTab === RECOMMENDATIONS_TABS.ACTIVE && isEmpty(updatedCategorizedActiveRecommendations)) ||
        (selectedTab === RECOMMENDATIONS_TABS.DISMISSED && isEmpty(updatedCategorizedDismissedRecommendations)) ||
        (selectedTab === RECOMMENDATIONS_TABS.EXCLUDED && isEmpty(updatedCategorizedExcludedRecommendations))
      ) {
        const newSelectedTabName = getNewSelectedTab(selectedTab, tabs);
        handleSuccessfulUpdate(newSelectedTabName);
      }
    }
  }, [categorizedRecommendations, isTabWrapperReady, recommendationCategory, selectedTab]);

  const handleAccordionsChange = (recommendationName) => {
    updateQueryParams({
      [RECOMMENDATION_TYPE_QUERY_PARAMETER]: recommendationName
    });
    updateExpanded(recommendationName);
    if (recommendationName) {
      getOptimizations({
        type: MAP_RECOMMENDATION_TYPES[recommendationName],
        limit: downloadLimit,
        status: getStatusBySelectedTab(selectedTab)
      });
    }
  };

  const handleTabChange = (event, value) => {
    setSelectedTab(value);
    handleAccordionsChange();
  };

  const updateCategoryAndSelectedTab = (newCategory) => {
    setRecommendationCategory(newCategory);

    const updateSelectedTab = () => {
      const isTargetCategorizedActiveOptimizationsEmpty = isEmpty(categorizedRecommendations[newCategory]?.active ?? {});
      const isTargetCategorizedDismissedOptimizationsEmpty = isEmpty(categorizedRecommendations[newCategory]?.dismissed ?? {});
      const isTargetCategorizedExcludedOptimizationsEmpty = isEmpty(categorizedRecommendations[newCategory]?.excluded ?? {});

      if (
        isTargetCategorizedActiveOptimizationsEmpty &&
        isTargetCategorizedDismissedOptimizationsEmpty &&
        isTargetCategorizedExcludedOptimizationsEmpty
      ) {
        return;
      }

      const tabs = [
        [RECOMMENDATIONS_TABS.ACTIVE, isTargetCategorizedActiveOptimizationsEmpty],
        [RECOMMENDATIONS_TABS.DISMISSED, isTargetCategorizedDismissedOptimizationsEmpty],
        [RECOMMENDATIONS_TABS.EXCLUDED, isTargetCategorizedExcludedOptimizationsEmpty]
      ];

      if (
        (selectedTab === RECOMMENDATIONS_TABS.ACTIVE && isTargetCategorizedActiveOptimizationsEmpty) ||
        (selectedTab === RECOMMENDATIONS_TABS.DISMISSED && isTargetCategorizedDismissedOptimizationsEmpty) ||
        (selectedTab === RECOMMENDATIONS_TABS.EXCLUDED && isTargetCategorizedExcludedOptimizationsEmpty)
      ) {
        const newSelectedTabName = getNewSelectedTab(selectedTab, tabs);
        handleTabChange({}, newSelectedTabName);
      }
    };
    updateSelectedTab();
  };

  useEffect(() => {
    if (isInitialMount && shouldInvoke) {
      const status = getStatusBySelectedTab(selectedTab);
      const type = MAP_RECOMMENDATION_TYPES[queryParamRecommendationType];
      const limit = type && downloadLimit;
      getOptimizations({ type, limit, status: type ? status : undefined });
    }
  }, [queryParamRecommendationType, isInitialMount, shouldInvoke, selectedTab, getOptimizations, downloadLimit]);

  useEffect(() => {
    setIsInitialMount(false);
  }, [setIsInitialMount]);

  const patchResource = (resourceId, recommendationType) =>
    dispatch((_, getState) => {
      dispatch(
        updateResourceVisibility(resourceId, {
          recommendation: recommendationType,
          action:
            selectedTab === RECOMMENDATIONS_TABS.ACTIVE
              ? RESOURCE_VISIBILITY_ACTIONS.DISMISS
              : RESOURCE_VISIBILITY_ACTIONS.ACTIVATE
        })
      ).then(() => {
        if (!isError(UPDATE_RESOURCE_VISIBILITY, getState())) {
          getOptimizations({
            type: recommendationType,
            limit: downloadLimit,
            status: getStatusBySelectedTab(selectedTab)
          });
        }
      });
    });

  const { isFileDownloading: isDownloadingCleanupScript, fetchAndDownload: fetchAndDownloadCleanupScripts } =
    useFetchAndDownload();
  const downloadCleanupScript = (moduleName, cloudAccount) => {
    fetchAndDownloadCleanupScripts({
      url: `${getApiUrl(RESTAPI)}/cloud_accounts/${cloudAccount}/cleanup_${moduleName}.sh`
    });
  };

  const { isFileDownloading: isDownloadingRecommendation, fetchAndDownload: fetchAndDownloadRecommendation } =
    useFetchAndDownload();
  const downloadRecommendation = (moduleName, format) => {
    const status = getStatusBySelectedTab(selectedTab);

    fetchAndDownloadRecommendation({
      url: `${getApiUrl(
        RESTAPI
      )}/organizations/${organizationId}/optimization_data?type=${moduleName}&status=${status}&format=${format}&limit=${downloadLimit}`,
      fallbackFilename: `${moduleName}.${format}`
    });
  };

  const applyFilterCallback = (dataSourceIds) => {
    const type = MAP_RECOMMENDATION_TYPES[queryParamRecommendationType];
    const limit = type && downloadLimit;
    let status;
    if (type) {
      status = getStatusBySelectedTab(selectedTab);
    }
    getOptimizations({ type, limit, status, dataSourceIds });
    setDataSourceIdsState(dataSourceIds);
  };

  const forceCheck = () => {
    dispatch(updateOptimizations(optimizations.id, { nextRun: FORCE_CHECK_NEXT_RUN }));
  };

  return (
    <Mocked mock={<RelevantRecommendationsMocked />} backdropMessageType={MESSAGE_TYPES.RECOMMENDATIONS}>
      <RelevantRecommendations
        isLoadingProps={{
          isGetRecommendationsLoading,
          isTabWrapperReady,
          isUpdateRecommendationsLoading,
          isGetResourceAllowedActionsLoading,
          isDownloadingRecommendation,
          isDownloadingCleanupScript
        }}
        selectedTab={selectedTab}
        handleTabChange={handleTabChange}
        patchResource={patchResource}
        data={optimizations}
        expanded={expanded}
        forceCheck={forceCheck}
        handleAccordionsChange={handleAccordionsChange}
        downloadRecommendation={downloadRecommendation}
        downloadCleanupScript={downloadCleanupScript}
        categorizedRecommendations={categorizedRecommendations}
        categoriesSizes={categoriesSizes}
        recommendationCategory={recommendationCategory}
        updateCategoryAndSelectedTab={updateCategoryAndSelectedTab}
        applyFilterCallback={applyFilterCallback}
      />
    </Mocked>
  );
};

const RelevantRecommendationsContainer = () => {
  const { useGetRecommendationsDownloadOptions } = OrganizationOptionsService();
  const { options: downloadOptions, isGetRecommendationsDownloadOptionsLoading } = useGetRecommendationsDownloadOptions();
  const downloadLimit = downloadOptions?.limit ?? RECOMMENDATIONS_LIMIT_FILTER;

  return isGetRecommendationsDownloadOptionsLoading ? (
    <ContentBackdropLoader isLoading />
  ) : (
    <RelevantRecommendationsDataContainer downloadLimit={downloadLimit} />
  );
};

export default RelevantRecommendationsContainer;

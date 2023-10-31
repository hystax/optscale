import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { RESTAPI, getResourceAllowedActions, updateResourceVisibility } from "api";
import { getOptimizationDetails } from "api/restapi/actionCreators";
import { GET_OPTIMIZATION_DETAILS } from "api/restapi/actionTypes";
import { ACTIVE } from "containers/RecommendationsOverviewContainer/recommendations/BaseRecommendation";
import { useAllRecommendations } from "hooks/useAllRecommendations";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { RESOURCE_VISIBILITY_ACTIONS } from "utils/constants";
import { isEmpty as isEmptyArray } from "utils/objects";

const useGetOptimizations = ({ type, limit, status, cloudAccountIds }) => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const { apiData: data } = useApiData(GET_OPTIMIZATION_DETAILS, {});

  const { isLoading, isDataReady, shouldInvoke } = useApiState(GET_OPTIMIZATION_DETAILS, {
    organizationId,
    cloudAccountIds,
    type,
    status,
    limit
  });

  const allRecommendations = useAllRecommendations();

  useEffect(() => {
    if (shouldInvoke) {
      dispatch((_, getState) => {
        dispatch(getOptimizationDetails(organizationId, { type, status, limit, cloudAccountIds })).then(() => {
          const newOptimizations = getState()?.[RESTAPI]?.[GET_OPTIMIZATION_DETAILS] ?? {};
          const recommendation = new allRecommendations[type](status, newOptimizations);

          if (!recommendation.dismissable) {
            return;
          }
          const ids = recommendation.items.map(({ resource_id: resourceId }) => resourceId).filter(Boolean);
          if (!isEmptyArray(ids)) {
            dispatch(getResourceAllowedActions(ids));
          }
        });
      });
    }
  }, [shouldInvoke, dispatch, organizationId, cloudAccountIds, limit, status, type, allRecommendations]);

  return { isLoading, isDataReady, data };
};

const usePatchResource = (recommendationType, status) => {
  const dispatch = useDispatch();

  return (resourceId) =>
    dispatch(
      updateResourceVisibility(resourceId, {
        recommendation: recommendationType,
        action: status === ACTIVE ? RESOURCE_VISIBILITY_ACTIONS.DISMISS : RESOURCE_VISIBILITY_ACTIONS.ACTIVATE
      })
    );
};

function RecommendationDetailsService() {
  return {
    useGetOptimizations,
    usePatchResource
  };
}

export default RecommendationDetailsService;

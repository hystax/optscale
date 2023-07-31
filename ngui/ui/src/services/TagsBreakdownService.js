import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getTagsBreakdown } from "api";
import { GET_TAGS_BREAKDOWN } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { mapCleanExpensesFilterParamsToApiParams } from "./CleanExpensesService";

const getParams = (filterParams) => ({
  ...mapCleanExpensesFilterParamsToApiParams(filterParams)
});

export const useGet = (params) => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const { apiData: data } = useApiData(GET_TAGS_BREAKDOWN);

  const { isLoading, shouldInvoke } = useApiState(GET_TAGS_BREAKDOWN, {
    organizationId,
    ...getParams(params)
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getTagsBreakdown(organizationId, getParams(params)));
    }
  }, [dispatch, organizationId, params, shouldInvoke]);

  return { isGetTagsBreakdownLoading: isLoading, data };
};

function TagsBreakdownService() {
  return { useGet };
}

export default TagsBreakdownService;

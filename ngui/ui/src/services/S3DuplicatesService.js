import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { createOrganizationGemini, getGemini, getOrganizationGeminis } from "api";
import { CREATE_ORGANIZATION_GEMINI, GET_GEMINI, GET_ORGANIZATION_GEMINIS } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useInScopeOfPageMockup } from "hooks/useInScopeOfPageMockup";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

const useGetAll = () => {
  const inScopeOfPageMockup = useInScopeOfPageMockup();

  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { geminis = [] }
  } = useApiData(GET_ORGANIZATION_GEMINIS);

  const { isLoading, shouldInvoke } = useApiState(GET_ORGANIZATION_GEMINIS, { organizationId });

  useEffect(() => {
    if (shouldInvoke && !inScopeOfPageMockup) {
      dispatch(getOrganizationGeminis(organizationId));
    }
  }, [dispatch, inScopeOfPageMockup, organizationId, shouldInvoke]);

  return { isLoading, geminis: inScopeOfPageMockup ? [] : geminis };
};

export const useGet = (checkId) => {
  const dispatch = useDispatch();

  const { apiData } = useApiData(GET_GEMINI);

  const { isLoading, shouldInvoke } = useApiState(GET_GEMINI, { checkId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getGemini(checkId));
    }
  }, [checkId, dispatch, shouldInvoke]);

  return { isLoading, gemini: apiData };
};

const useCreate = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_ORGANIZATION_GEMINI);

  const onCreate = (params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(createOrganizationGemini(organizationId, params)).then(() => {
          if (!isError(CREATE_ORGANIZATION_GEMINI, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onCreate, isLoading };
};

function S3DuplicatesService() {
  return { useGetAll, useGet, useCreate };
}

export default S3DuplicatesService;

import { useCallback } from "react";
import { useDispatch } from "react-redux";
import { createSurvey as createSurveyApi } from "api";
import { CREATE_SURVEY } from "api/restapi/actionTypes";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { checkError } from "utils/api";

export const SURVEY_TYPES = Object.freeze({
  DISCONNECT_LAST_DATA_SOURCE: "disconnect_last_account"
});

const useCreateSurvey = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { isLoading } = useApiState(CREATE_SURVEY);

  const createSurvey = useCallback(
    (type, survey) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(createSurveyApi(organizationId, { type, survey }))
            .then(() => checkError(CREATE_SURVEY, getState()))
            .then(() => resolve())
            .catch(() => reject());
        });
      }),
    [dispatch, organizationId]
  );

  return { isLoading, createSurvey };
};

function SurveyService() {
  return { useCreateSurvey };
}

export default SurveyService;

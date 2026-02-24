import { useDispatch } from "react-redux";
import { updateDataSource, createSurvey as createSurveyApi } from "api";
import { UPDATE_DATA_SOURCE, CREATE_SURVEY } from "api/restapi/actionTypes";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { checkError } from "utils/api";

export const DATASOURCE_SURVEY_TYPES = Object.freeze({
  DISCONNECT_LAST_DATA_SOURCE: "disconnect_last_account",
});

const useUpdateDataSource = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(UPDATE_DATA_SOURCE);

  const onUpdate = (id, params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updateDataSource(id, params))
          .then(() => checkError(UPDATE_DATA_SOURCE, getState()))
          .then(() => resolve())
          .catch(() => reject());
      });
    });

  return { onUpdate, isLoading };
};

const useCreateSurvey = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { isLoading } = useApiState(CREATE_SURVEY);

  const createSurvey = (type, payload) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(createSurveyApi(organizationId, { type, payload }))
          .then(() => checkError(CREATE_SURVEY, getState()))
          .then(() => resolve())
          .catch(() => reject());
      });
    });

  return { isLoading, createSurvey };
};

function DataSourcesService() {
  return {
    useUpdateDataSource,
    useCreateSurvey,
  };
}

export default DataSourcesService;

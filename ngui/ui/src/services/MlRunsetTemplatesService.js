import { useEffect } from "react";
import { useDispatch } from "react-redux";
import {
  createMlRunsetTemplate,
  getMlRunsetTemplates,
  updateMlRunsetTemplate,
  getMlRunsetTemplate,
  deleteMlRunsetTemplate
} from "api";
import {
  CREATE_ML_RUNSET_TEMPLATE,
  DELETE_ML_RUNSET_TEMPLATE,
  GET_ML_RUNSET_TEMPLATE,
  GET_ML_RUNSET_TEMPLATES,
  UPDATE_ML_RUNSET_TEMPLATE
} from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

const useGetAll = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { templates: runsetTemplates = [] }
  } = useApiData(GET_ML_RUNSET_TEMPLATES);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_RUNSET_TEMPLATES, { organizationId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlRunsetTemplates(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  return { isLoading, runsetTemplates };
};

const useGetOne = (runsetTemplateId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData } = useApiData(GET_ML_RUNSET_TEMPLATE);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_RUNSET_TEMPLATE, { organizationId, runsetTemplateId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlRunsetTemplate(organizationId, runsetTemplateId));
    }
  }, [dispatch, organizationId, runsetTemplateId, shouldInvoke]);

  return { isLoading, runsetTemplate: apiData };
};

const useCreateMlRunsetTemplate = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_ML_RUNSET_TEMPLATE);

  const onCreate = (params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(createMlRunsetTemplate(organizationId, params)).then(() => {
          if (!isError(CREATE_ML_RUNSET_TEMPLATE, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onCreate, isLoading };
};

const useUpdateRunsetTemplate = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(UPDATE_ML_RUNSET_TEMPLATE);

  const onUpdate = (runsetTemplateId, params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updateMlRunsetTemplate(organizationId, runsetTemplateId, params)).then(() => {
          if (!isError(UPDATE_ML_RUNSET_TEMPLATE, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onUpdate, isLoading };
};

const useDeleteMlRunsetTemplate = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(DELETE_ML_RUNSET_TEMPLATE);

  const onDelete = (runsetTemplateId) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(deleteMlRunsetTemplate(organizationId, runsetTemplateId)).then(() => {
          if (!isError(DELETE_ML_RUNSET_TEMPLATE, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onDelete, isLoading };
};

function MlRunsetTemplatesService() {
  return { useGetAll, useGetOne, useCreateMlRunsetTemplate, useDeleteMlRunsetTemplate, useUpdateRunsetTemplate };
}

export default MlRunsetTemplatesService;

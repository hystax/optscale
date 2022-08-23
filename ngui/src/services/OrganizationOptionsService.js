import { useEffect, useMemo } from "react";
import { useDispatch } from "react-redux";
import {
  getOptimizationOptions,
  updateOptimizationOptions,
  getFinOpsAssessment,
  updateFinOpsAssessment,
  getTechnicalAudit,
  updateTechnicalAudit,
  getOrganizationOptions,
  getOrganizationOption,
  updateOrganizationOption,
  createOrganizationOption,
  deleteOrganizationOption
} from "api";
import { getRecommendationsDownloadLimit, updateOrganizationThemeSettings } from "api/restapi/actionCreators";
import {
  GET_ORGANIZATION_OPTIONS,
  GET_ORGANIZATION_OPTION,
  GET_OPTIMIZATION_OPTIONS,
  UPDATE_OPTIMIZATION_OPTIONS,
  GET_FINOPS_ASSESSMENT,
  UPDATE_FINOPS_ASSESSMENT,
  GET_TECHNICAL_AUDIT,
  UPDATE_TECHNICAL_AUDIT,
  UPDATE_ORGANIZATION_OPTION,
  CREATE_ORGANIZATION_OPTION,
  DELETE_ORGANIZATION_OPTION,
  GET_RECOMMENDATIONS_DOWNLOAD_OPTIONS,
  UPDATE_ORGANIZATION_THEME_SETTINGS
} from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError, checkError } from "utils/api";
import { parseJSON } from "utils/strings";

export const useGet = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { apiData: options } = useApiData(GET_ORGANIZATION_OPTIONS, []);

  const { isLoading, shouldInvoke } = useApiState(GET_ORGANIZATION_OPTIONS, organizationId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getOrganizationOptions(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  return { isGetOrganizationOptionsLoading: isLoading, options };
};

export const useGetOption = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { apiData: value } = useApiData(GET_ORGANIZATION_OPTION, "{}");

  const jsonValue = useMemo(() => parseJSON(value), [value]);

  const { isLoading } = useApiState(GET_ORGANIZATION_OPTION);

  const getOption = (name) => dispatch(getOrganizationOption(organizationId, name));

  return { isGetOrganizationOptionLoading: isLoading, value: jsonValue, getOption };
};

export const useDeleteOption = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { isLoading } = useApiState(DELETE_ORGANIZATION_OPTION);

  const deleteOption = (name, onSuccess) => {
    dispatch((_, getState) => {
      dispatch(deleteOrganizationOption(organizationId, name))
        .then(() => checkError(DELETE_ORGANIZATION_OPTION, getState()))
        .then(() => {
          if (typeof onSuccess === "function") {
            onSuccess();
          }
        });
    });
  };

  return { isDeleteOrganizationOptionLoading: isLoading, deleteOption };
};

export const useUpdateOption = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { isLoading } = useApiState(UPDATE_ORGANIZATION_OPTION);

  const updateOption = (name, value, onSuccess) => {
    dispatch((_, getState) => {
      dispatch(updateOrganizationOption(organizationId, name, value))
        .then(() => checkError(UPDATE_ORGANIZATION_OPTION, getState()))
        .then(() => {
          if (typeof onSuccess === "function") {
            onSuccess();
          }
        });
    });
  };

  return { isUpdateOrganizationOptionLoading: isLoading, updateOption };
};

export const useUpdateThemeSettings = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { isLoading } = useApiState(UPDATE_ORGANIZATION_THEME_SETTINGS);

  const update = (value) => {
    dispatch((_, getState) => {
      dispatch(updateOrganizationThemeSettings(organizationId, value)).then(() =>
        checkError(UPDATE_ORGANIZATION_THEME_SETTINGS, getState())
      );
    });
  };

  return { isLoading, update };
};

export const useCreateOption = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { isLoading } = useApiState(CREATE_ORGANIZATION_OPTION);

  const createOption = (name, value, onSuccess) => {
    dispatch((_, getState) => {
      dispatch(createOrganizationOption(organizationId, name, value))
        .then(() => checkError(CREATE_ORGANIZATION_OPTION, getState()))
        .then(() => {
          if (typeof onSuccess === "function") {
            onSuccess();
          }
        });
    });
  };

  return { isCreateOrganizationOptionLoading: isLoading, createOption };
};

export const useGetRecommendationOptions = (recommendationType) => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { apiData: options } = useApiData(GET_OPTIMIZATION_OPTIONS, {});

  const { isLoading, shouldInvoke } = useApiState(GET_OPTIMIZATION_OPTIONS, {
    organizationId,
    recommendationType
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getOptimizationOptions(organizationId, recommendationType));
    }
  }, [dispatch, organizationId, recommendationType, shouldInvoke]);

  return { isLoading, options };
};

export const useGetRecommendationOptionsOnce = (recommendationType) => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { apiData: options } = useApiData(GET_OPTIMIZATION_OPTIONS, {});

  const { isLoading } = useApiState(GET_OPTIMIZATION_OPTIONS, {
    organizationId,
    recommendationType
  });

  useEffect(() => {
    dispatch(getOptimizationOptions(organizationId, recommendationType));
  }, [dispatch, organizationId, recommendationType]);

  return { isLoading, options };
};

export const useUpdateRecommendationOptions = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { isLoading } = useApiState(UPDATE_OPTIMIZATION_OPTIONS);

  const updateRecommendationOptions = (recommendationType, payload = {}, onSuccess) => {
    const pathParams = { organizationId, recommendationType };

    const { options, settingType } = payload;

    const params = {
      value: JSON.stringify(options)
    };

    dispatch((_, getState) => {
      dispatch(updateOptimizationOptions(settingType, pathParams, params)).then(() => {
        if (typeof onSuccess === "function" && !isError(UPDATE_OPTIMIZATION_OPTIONS, getState())) {
          onSuccess();
        }
        return undefined;
      });
    });
  };

  return { isLoading, updateRecommendationOptions };
};

export const useGetFinOpsAssessment = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { value: options = "{}" }
  } = useApiData(GET_FINOPS_ASSESSMENT, {});

  const { isLoading, shouldInvoke, isDataReady } = useApiState(GET_FINOPS_ASSESSMENT, organizationId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getFinOpsAssessment(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  return { options: parseJSON(options), isGetFinOpsAssessmentLoading: isLoading, isGetFinOpsAssessmentDataReady: isDataReady };
};

export const useUpdateFinOpsAssessment = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading } = useApiState(UPDATE_FINOPS_ASSESSMENT);

  const {
    apiData: { value: options = "{}" }
  } = useApiData(GET_FINOPS_ASSESSMENT, {});

  const update = (value = {}) => {
    const resultValue = {
      ...parseJSON(options),
      ...value
    };

    dispatch(updateFinOpsAssessment(organizationId, resultValue));
  };

  const reset = () => dispatch(updateFinOpsAssessment(organizationId, { step: 0 }));

  return { update, reset, isUpdateFinOpsAssessmentLoading: isLoading };
};

export const useGetTechnicalAudit = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { value: options = "{}" }
  } = useApiData(GET_TECHNICAL_AUDIT, {});

  const { isLoading, shouldInvoke, isDataReady } = useApiState(GET_TECHNICAL_AUDIT, organizationId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getTechnicalAudit(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  return { options: parseJSON(options), isGetTechnicalAuditLoading: isLoading, isGetTechnicalAuditDataReady: isDataReady };
};

export const useUpdateTechnicalAudit = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading } = useApiState(UPDATE_TECHNICAL_AUDIT);

  const {
    apiData: { value: options = "{}" }
  } = useApiData(GET_TECHNICAL_AUDIT, {});

  const update = (value = {}) => {
    const { codeReportFiles: storedCodeReportFiles = [], ...restStoredOptions } = parseJSON(options);

    const { codeReportFiles = [], ...restValues } = value;
    const resultValue = {
      ...restStoredOptions,
      ...restValues,
      codeReportFiles: [...storedCodeReportFiles, ...codeReportFiles]
    };

    dispatch(updateTechnicalAudit(organizationId, resultValue));
  };

  const reset = () => dispatch(updateTechnicalAudit(organizationId, { step: 0 }));

  return { update, reset, isUpdateTechnicalAuditLoading: isLoading };
};

export const useGetRecommendationsDownloadOptions = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { value: options = "{}" }
  } = useApiData(GET_RECOMMENDATIONS_DOWNLOAD_OPTIONS, {});

  const { isLoading, shouldInvoke, isDataReady } = useApiState(GET_RECOMMENDATIONS_DOWNLOAD_OPTIONS, organizationId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getRecommendationsDownloadLimit(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  return {
    options: parseJSON(options),
    isGetRecommendationsDownloadOptionsLoading: isLoading,
    isGetRecommendationsDownloadOptionsReady: isDataReady
  };
};

function OrganizationOptionsService() {
  return {
    useGet,
    useGetOption,
    useUpdateOption,
    useCreateOption,
    useDeleteOption,
    useGetRecommendationOptions,
    useGetRecommendationOptionsOnce,
    useUpdateRecommendationOptions,
    useGetFinOpsAssessment,
    useUpdateFinOpsAssessment,
    useGetTechnicalAudit,
    useUpdateTechnicalAudit,
    useGetRecommendationsDownloadOptions,
    useUpdateThemeSettings
  };
}

export default OrganizationOptionsService;

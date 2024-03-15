import { useEffect, useMemo } from "react";
import { useDispatch } from "react-redux";
import {
  getOptimizationOptions,
  updateOptimizationOptions,
  getOrganizationOptions,
  getOrganizationOption,
  updateOrganizationOption,
  createOrganizationOption,
  deleteOrganizationOption
} from "api";
import {
  getRecommendationsDownloadLimit,
  updateOrganizationThemeSettings,
  updateOrganizationPerspectives,
  getS3DuplicatesOrganizationSettings,
  updateS3DuplicatesOrganizationSettings
} from "api/restapi/actionCreators";
import {
  GET_ORGANIZATION_OPTIONS,
  GET_ORGANIZATION_OPTION,
  GET_OPTIMIZATION_OPTIONS,
  UPDATE_OPTIMIZATION_OPTIONS,
  UPDATE_ORGANIZATION_OPTION,
  CREATE_ORGANIZATION_OPTION,
  DELETE_ORGANIZATION_OPTION,
  GET_RECOMMENDATIONS_DOWNLOAD_OPTIONS,
  UPDATE_ORGANIZATION_THEME_SETTINGS,
  UPDATE_ORGANIZATION_PERSPECTIVES,
  GET_S3_DUPLICATES_ORGANIZATION_SETTINGS,
  UPDATE_S3_DUPLICATES_ORGANIZATION_SETTINGS
} from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError, checkError } from "utils/api";
import { parseJSON } from "utils/strings";

const useGet = (withValues) => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { apiData: options } = useApiData(GET_ORGANIZATION_OPTIONS, []);

  const { isLoading, shouldInvoke } = useApiState(GET_ORGANIZATION_OPTIONS, { organizationId, withValues });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getOrganizationOptions(organizationId, withValues));
    }
  }, [dispatch, organizationId, withValues, shouldInvoke]);

  return {
    isGetOrganizationOptionsLoading: isLoading,
    options: withValues ? options.map(({ name, value }) => ({ name, value: parseJSON(value) })) : options
  };
};

const useGetOption = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { apiData: value } = useApiData(GET_ORGANIZATION_OPTION, "{}");

  const jsonValue = useMemo(() => parseJSON(value), [value]);

  const { isLoading } = useApiState(GET_ORGANIZATION_OPTION);

  const getOption = (name) => dispatch(getOrganizationOption(organizationId, name));

  return { isGetOrganizationOptionLoading: isLoading, value: jsonValue, getOption };
};

// TODO - useGetOption return a dispatch function, which is unconvenoent to use, created not to break useGetOption, combine or rewrite.
const useGetByName = (name) => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { apiData: option } = useApiData(GET_ORGANIZATION_OPTION, "{}");

  const { isLoading, shouldInvoke } = useApiState(GET_ORGANIZATION_OPTION, { organizationId, name });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getOrganizationOption(organizationId, name));
    }
  }, [dispatch, organizationId, name, shouldInvoke]);

  return {
    isGetOrganizationOptionLoading: isLoading,
    option: parseJSON(option)
  };
};

const useDeleteOption = () => {
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

const useUpdateOption = () => {
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

const useUpdateThemeSettings = () => {
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

const useCreateOption = () => {
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

const useGetRecommendationOptions = (recommendationType) => {
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

const useGetRecommendationOptionsOnce = (recommendationType) => {
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

const useUpdateRecommendationOptions = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { isLoading } = useApiState(UPDATE_OPTIMIZATION_OPTIONS);

  const updateRecommendationOptions = (recommendationType, payload = {}, onSuccess) => {
    const pathParams = { organizationId, recommendationType };

    const { options, settingType } = payload;

    // isUpdated field is set to true on every update
    // to identify if actual recommendaition options are "outdated" (see BaseRecommendation -> optionsInSync)
    // This field will be removed on the next recomendaition check, because it is "artificial" and
    // is not recognized by any recommendation type.
    const params = {
      value: JSON.stringify({ ...options, isUpdated: true })
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

const useUpdateOrganizationPerspectives = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { isLoading } = useApiState(UPDATE_ORGANIZATION_PERSPECTIVES);

  const update = (value, onSuccess) => {
    dispatch((_, getState) => {
      dispatch(updateOrganizationPerspectives(organizationId, value))
        .then(() => checkError(UPDATE_ORGANIZATION_PERSPECTIVES, getState()))
        .then(() => {
          if (typeof onSuccess === "function") {
            onSuccess();
          }
        });
    });
  };

  return { isLoading, update };
};

const useGetRecommendationsDownloadOptions = () => {
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

const useGetS3DuplicatesOrganizationSettings = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { apiData: options } = useApiData(GET_S3_DUPLICATES_ORGANIZATION_SETTINGS, {});

  const { isLoading, shouldInvoke } = useApiState(GET_S3_DUPLICATES_ORGANIZATION_SETTINGS, organizationId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getS3DuplicatesOrganizationSettings(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  return { isLoading, options };
};

const useUpdateS3DuplicatedOrganizationSettings = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { isLoading } = useApiState(UPDATE_S3_DUPLICATES_ORGANIZATION_SETTINGS);

  const onUpdate = (value) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updateS3DuplicatesOrganizationSettings(organizationId, value)).then(() => {
          if (!isError(UPDATE_S3_DUPLICATES_ORGANIZATION_SETTINGS, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onUpdate, isLoading };
};

function OrganizationOptionsService() {
  return {
    useGet,
    useGetOption,
    useGetByName,
    useUpdateOption,
    useCreateOption,
    useDeleteOption,
    useGetRecommendationOptions,
    useGetRecommendationOptionsOnce,
    useUpdateRecommendationOptions,
    useGetRecommendationsDownloadOptions,
    useUpdateThemeSettings,
    useUpdateOrganizationPerspectives,
    useGetS3DuplicatesOrganizationSettings,
    useUpdateS3DuplicatedOrganizationSettings
  };
}

export default OrganizationOptionsService;

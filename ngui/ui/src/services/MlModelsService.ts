import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { createMlModel, deleteMlModel, getMlModel, getMlModels, updateMlModel, updateMlModelVersion } from "api";
import {
  CREATE_ML_MODEL,
  DELETE_ML_MODEL,
  GET_ML_MODEL,
  GET_ML_MODELS,
  UPDATE_ML_MODEL,
  UPDATE_ML_MODEL_VERSION
} from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

type Version = {
  id: string;
  path: string;
  aliases: string[];
  version: string;
  tags: { [key: string]: string };
  created_at: number;
};

type Model = {
  key: string;
  name: string;
  description: string;
  tags: { [key: string]: string };
  created_at: number;
  id: string;
};

export type ListModel = Model & {
  // Last version can be an empty object
  last_version: Partial<Version>;
  aliased_versions: (Omit<Version, "aliases"> & { alias: string })[];
};

export type ModelVersion = Version & {
  run: {
    name: string;
    task_id: string;
    number: number;
    id: string;
  };
};

export type ModelDetails = Model & {
  versions: ModelVersion[];
};

export type ModelVersionWithModel = ModelVersion & {
  model: Model;
};

export type CreateModelApiParams = Pick<Model, "name" | "key" | "description" | "tags">;

export type EditModelApiParams = Partial<Pick<Model, "name" | "description" | "tags">>;

export type EditVersionApiParams = Partial<Pick<Version, "aliases" | "path" | "tags">>;

const useGetAll = (): {
  isLoading: boolean;
  models: ListModel[];
} => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { models = [] }
  } = useApiData(GET_ML_MODELS);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_MODELS, organizationId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlModels(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  return {
    isLoading,
    models
  };
};

const useGet = (
  modelId: string
): {
  isLoading: boolean;
  model: ModelDetails;
} => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: model } = useApiData(GET_ML_MODEL);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_MODEL, { organizationId, modelId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlModel(organizationId, modelId));
    }
  }, [dispatch, modelId, organizationId, shouldInvoke]);

  return {
    isLoading,
    model
  };
};

const useCreate = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_ML_MODEL);

  const onCreate = (params: CreateModelApiParams): Promise<void> =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(createMlModel(organizationId, params)).then(() => {
          if (!isError(CREATE_ML_MODEL, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onCreate, isLoading };
};

const useUpdate = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(UPDATE_ML_MODEL);

  const onUpdate = (modelId: string, params: EditModelApiParams): Promise<void> =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updateMlModel(organizationId, modelId, params)).then(() => {
          if (!isError(UPDATE_ML_MODEL, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onUpdate, isLoading };
};

const useDelete = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(DELETE_ML_MODEL);

  const onDelete = (modelId: string): Promise<void> =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(deleteMlModel(organizationId, modelId)).then(() => {
          if (!isError(DELETE_ML_MODEL, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onDelete, isLoading };
};

const useUpdateModelVersion = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(UPDATE_ML_MODEL_VERSION);

  const onUpdate = (modelId: string, runId: string, params: EditVersionApiParams): Promise<void> =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updateMlModelVersion(organizationId, modelId, runId, params)).then(() => {
          if (!isError(UPDATE_ML_MODEL_VERSION, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onUpdate, isLoading };
};

function MlModelsService() {
  return {
    useGetAll,
    useGet,
    useCreate,
    useUpdate,
    useDelete,
    useUpdateModelVersion
  };
}

export default MlModelsService;

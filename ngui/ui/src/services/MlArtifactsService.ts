import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { createMlArtifact, deleteMlArtifact, getMlArtifact, getMlArtifacts, updateMlArtifact } from "api";
import {
  CREATE_ML_ARTIFACT,
  DELETE_ML_ARTIFACT,
  GET_ML_ARTIFACT,
  GET_ML_ARTIFACTS,
  UPDATE_ML_ARTIFACT
} from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

export type Artifact = {
  path: string;
  name: string;
  description: string;
  tags: Record<string, string>;
  created_at: number;
  run: {
    task_id: string;
    name: string;
    number: number;
    id: string;
  };
  id: string;
};

type GetApiParams = {
  runId?: string | string[];
  limit?: number;
  startFrom?: number;
  textLike?: string;
  createdAtGt: number;
  createdAtLt: number;
};

type EditApplicationApiParams = {
  name?: string;
  path?: string;
  description?: string;
  tags?: Record<string, string>;
};

type CreateApplicationApiParams = {
  name?: string;
  path?: string;
  description?: string;
  tags?: Record<string, string>;
};

const useGet = (
  params?: GetApiParams
): {
  isLoading: boolean;
  data: {
    artifacts?: Artifact[];
    limit?: number;
    start_from?: number;
    total_count?: number;
  };
} => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData } = useApiData(GET_ML_ARTIFACTS);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_ARTIFACTS, { organizationId, ...params });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlArtifacts(organizationId, params));
    }
  }, [dispatch, organizationId, params, shouldInvoke]);

  return { isLoading, data: apiData };
};

const useGetOne = (
  artifactId: string
): {
  isLoading: boolean;
  artifact: Partial<Artifact>;
} => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData } = useApiData(GET_ML_ARTIFACT);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_ARTIFACT, { organizationId, artifactId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlArtifact(organizationId, artifactId));
    }
  }, [artifactId, dispatch, organizationId, shouldInvoke]);

  return { isLoading, artifact: apiData };
};

const useUpdate = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(UPDATE_ML_ARTIFACT);

  const onUpdate = (applicationId: string, params: EditApplicationApiParams): Promise<void> =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updateMlArtifact(organizationId, applicationId, params)).then(() => {
          if (!isError(UPDATE_ML_ARTIFACT, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onUpdate, isLoading };
};

const useCreate = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_ML_ARTIFACT);

  const onCreate = (params: CreateApplicationApiParams): Promise<void> =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(createMlArtifact(organizationId, params)).then(() => {
          if (!isError(CREATE_ML_ARTIFACT, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onCreate, isLoading };
};

const useDelete = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(DELETE_ML_ARTIFACT);

  const onDelete = (artifactId: string): Promise<void> =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(deleteMlArtifact(organizationId, artifactId)).then(() => {
          if (!isError(DELETE_ML_ARTIFACT, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onDelete, isLoading };
};

function MlArtifactsService() {
  return {
    useGet,
    useGetOne,
    useUpdate,
    useCreate,
    useDelete
  };
}

export default MlArtifactsService;

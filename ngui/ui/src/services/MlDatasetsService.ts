import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getMlDatasets, createMlDataset, getMlDataset, updateMlDataset, deleteMlDataset } from "api";
import {
  GET_ML_DATASETS,
  CREATE_ML_DATASET,
  GET_ML_DATASET,
  UPDATE_ML_DATASET,
  DELETE_ML_DATASET
} from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

const useGet = (datasetId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: dataset = {} } = useApiData(GET_ML_DATASET);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_DATASET, { organizationId, datasetId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlDataset(organizationId, datasetId));
    }
  }, [dispatch, organizationId, datasetId, shouldInvoke]);

  return { isLoading, dataset };
};

const useGetAll = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { datasets = [] }
  } = useApiData(GET_ML_DATASETS);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_DATASETS, organizationId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlDatasets(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  return { isLoading, datasets };
};

const useCreate = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_ML_DATASET);

  const onCreate = (params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(createMlDataset(organizationId, params)).then(() => {
          if (!isError(CREATE_ML_DATASET, getState())) {
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
  const { isLoading } = useApiState(UPDATE_ML_DATASET);

  const onUpdate = (id, params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updateMlDataset(organizationId, id, params)).then(() => {
          if (!isError(UPDATE_ML_DATASET, getState())) {
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
  const { isLoading } = useApiState(DELETE_ML_DATASET);

  const onDelete = (id) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(deleteMlDataset(organizationId, id)).then(() => {
          if (!isError(DELETE_ML_DATASET, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onDelete, isLoading };
};

function MlDatasetsService() {
  return {
    useGetAll,
    useGet,
    useCreate,
    useUpdate,
    useDelete
  };
}

export default MlDatasetsService;

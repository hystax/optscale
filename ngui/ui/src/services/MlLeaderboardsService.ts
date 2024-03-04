import { useCallback, useEffect } from "react";
import { useDispatch } from "react-redux";
import {
  getMlLeaderboards,
  createMlLeaderboard,
  getMlLeaderboardDatasetInfo as getMlLeaderboardDatasetDetails,
  updateMlLeaderboard,
  getMlLeaderboardDatasets,
  createMlLeaderboardDataset,
  updateMlLeaderboardDataset,
  deleteMlLeaderboardDataset,
  getMlLeaderboardDataset,
  RESTAPI
} from "api";
import {
  GET_ML_LEADERBOARD,
  CREATE_ML_LEADERBOARD,
  GET_ML_LEADERBOARD_DATASET_DETAILS,
  UPDATE_ML_LEADERBOARD,
  GET_ML_LEADERBOARD_DATASETS,
  CREATE_ML_LEADERBOARD_DATASET,
  UPDATE_ML_LEADERBOARD_DATASET,
  DELETE_ML_LEADERBOARD_DATASET,
  GET_ML_LEADERBOARD_DATASET
} from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

const useGetLeaderboard = (taskId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: leaderboard } = useApiData(GET_ML_LEADERBOARD);

  const { isLoading, isDataReady, shouldInvoke } = useApiState(GET_ML_LEADERBOARD, { organizationId, taskId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlLeaderboards(organizationId, taskId));
    }
  }, [dispatch, organizationId, shouldInvoke, taskId]);

  return {
    isLoading,
    isDataReady,
    leaderboard
  };
};

const useGetLeaderboardOnDemand = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading } = useApiState(GET_ML_LEADERBOARD);

  const { apiData: leaderboard } = useApiData(GET_ML_LEADERBOARD);

  const getData = useCallback(
    (taskId) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(getMlLeaderboards(organizationId, taskId)).then(() => {
            if (!isError(GET_ML_LEADERBOARD, getState())) {
              const apiData = getState()?.[RESTAPI]?.[GET_ML_LEADERBOARD];
              return resolve(apiData);
            }
            return reject();
          });
        });
      }),
    [dispatch, organizationId]
  );

  return { isLoading, data: leaderboard, getData };
};
const useCreateLeaderboard = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_ML_LEADERBOARD);

  const onCreate = useCallback(
    (taskId, params) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(createMlLeaderboard(organizationId, taskId, params)).then(() => {
            if (!isError(CREATE_ML_LEADERBOARD, getState())) {
              return resolve();
            }
            return reject();
          });
        });
      }),
    [dispatch, organizationId]
  );

  return { onCreate, isLoading };
};

const useUpdateLeaderboard = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(UPDATE_ML_LEADERBOARD);

  const onUpdate = useCallback(
    (id, params) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(updateMlLeaderboard(organizationId, id, params)).then(() => {
            if (!isError(UPDATE_ML_LEADERBOARD, getState())) {
              return resolve();
            }
            return reject();
          });
        });
      }),
    [dispatch, organizationId]
  );

  return { onUpdate, isLoading };
};

const useGetLeaderboardDatasets = (leaderboardId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: leaderboardDatasets } = useApiData(GET_ML_LEADERBOARD_DATASETS, []);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_LEADERBOARD_DATASETS, { organizationId, leaderboardId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlLeaderboardDatasets(organizationId, leaderboardId));
    }
  }, [dispatch, organizationId, shouldInvoke, leaderboardId]);

  return {
    isLoading,
    leaderboardDatasets
  };
};

const useGetLeaderboardDatasetsOnDemand = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: data } = useApiData(GET_ML_LEADERBOARD_DATASETS, []);

  const { isLoading } = useApiState(GET_ML_LEADERBOARD_DATASETS);

  const getData = useCallback(
    (leaderboardId) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(getMlLeaderboardDatasets(organizationId, leaderboardId)).then(() => {
            if (!isError(GET_ML_LEADERBOARD_DATASETS, getState())) {
              const apiData = getState()?.[RESTAPI]?.[GET_ML_LEADERBOARD_DATASETS];
              return resolve(apiData);
            }
            return reject();
          });
        });
      }),
    [dispatch, organizationId]
  );

  return {
    isLoading,
    data,
    getData
  };
};

const useGetLeaderboardDataset = (leaderboardDatasetId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: leaderboardDataset } = useApiData(GET_ML_LEADERBOARD_DATASET);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_LEADERBOARD_DATASET, { organizationId, leaderboardDatasetId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlLeaderboardDataset(organizationId, leaderboardDatasetId));
    }
  }, [dispatch, organizationId, shouldInvoke, leaderboardDatasetId]);

  return {
    isLoading,
    leaderboardDataset
  };
};

const useGetLeaderboardDatasetOnDemand = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: leaderboardDataset } = useApiData(GET_ML_LEADERBOARD_DATASET);

  const { isLoading } = useApiState(GET_ML_LEADERBOARD_DATASET);

  const getData = useCallback(
    (leaderboardDatasetId) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(getMlLeaderboardDataset(organizationId, leaderboardDatasetId)).then(() => {
            if (!isError(GET_ML_LEADERBOARD_DATASET, getState())) {
              const apiData = getState()?.[RESTAPI]?.[GET_ML_LEADERBOARD_DATASET];
              return resolve(apiData);
            }
            return reject();
          });
        });
      }),
    [dispatch, organizationId]
  );

  return {
    isLoading,
    getData,
    data: leaderboardDataset
  };
};

const useCreateLeaderboardDataset = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_ML_LEADERBOARD_DATASET);

  const onCreate = useCallback(
    (leaderboardId, params) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(createMlLeaderboardDataset(organizationId, leaderboardId, params)).then(() => {
            if (!isError(CREATE_ML_LEADERBOARD_DATASET, getState())) {
              return resolve();
            }
            return reject();
          });
        });
      }),
    [dispatch, organizationId]
  );

  return { onCreate, isLoading };
};

const useUpdateLeaderboardDataset = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(UPDATE_ML_LEADERBOARD_DATASET);

  const onUpdate = useCallback(
    (leaderboardDatasetId, params) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(updateMlLeaderboardDataset(organizationId, leaderboardDatasetId, params)).then(() => {
            if (!isError(UPDATE_ML_LEADERBOARD_DATASET, getState())) {
              return resolve();
            }
            return reject();
          });
        });
      }),
    [dispatch, organizationId]
  );

  return { onUpdate, isLoading };
};

const useDeleteLeaderboardDataset = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(DELETE_ML_LEADERBOARD_DATASET);

  const onDelete = useCallback(
    (leaderboardDatasetId) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(deleteMlLeaderboardDataset(organizationId, leaderboardDatasetId)).then(() => {
            if (!isError(DELETE_ML_LEADERBOARD_DATASET, getState())) {
              return resolve();
            }
            return reject();
          });
        });
      }),
    [dispatch, organizationId]
  );

  return { onDelete, isLoading };
};

const useGetLeaderboardDatasetDetails = (leaderboardDatasetId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: leaderboardDatasetDetails } = useApiData(GET_ML_LEADERBOARD_DATASET_DETAILS, []);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_LEADERBOARD_DATASET_DETAILS, { organizationId, leaderboardDatasetId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlLeaderboardDatasetDetails(organizationId, leaderboardDatasetId));
    }
  }, [dispatch, organizationId, leaderboardDatasetId, shouldInvoke]);

  return {
    isLoading,
    leaderboardDatasetDetails
  };
};

const useGetLeaderboardDatasetDetailsOnDemand = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: leaderboardDatasetDetails } = useApiData(GET_ML_LEADERBOARD_DATASET_DETAILS, []);

  const { isLoading } = useApiState(GET_ML_LEADERBOARD_DATASET_DETAILS);

  const getData = useCallback(
    (leaderboardDatasetId) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(getMlLeaderboardDatasetDetails(organizationId, leaderboardDatasetId)).then(() => {
            if (!isError(GET_ML_LEADERBOARD_DATASET_DETAILS, getState())) {
              const apiData = getState()?.[RESTAPI]?.[GET_ML_LEADERBOARD_DATASET_DETAILS];
              return resolve(apiData);
            }
            return reject();
          });
        });
      }),
    [dispatch, organizationId]
  );

  return {
    isLoading,
    getData,
    data: leaderboardDatasetDetails
  };
};

function MlLeaderboardsService() {
  return {
    useGetLeaderboard,
    useGetLeaderboardOnDemand,
    useCreateLeaderboard,
    useUpdateLeaderboard,

    useGetLeaderboardDatasets,
    useGetLeaderboardDatasetsOnDemand,

    useGetLeaderboardDataset,
    useGetLeaderboardDatasetOnDemand,
    useCreateLeaderboardDataset,
    useUpdateLeaderboardDataset,
    useDeleteLeaderboardDataset,

    useGetLeaderboardDatasetDetails,
    useGetLeaderboardDatasetDetailsOnDemand
  };
}

export default MlLeaderboardsService;

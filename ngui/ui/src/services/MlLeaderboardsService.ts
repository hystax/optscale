import { useCallback, useEffect } from "react";
import { useDispatch } from "react-redux";
import {
  getMlLeaderboardTemplate,
  createMlLeaderboardTemplate,
  getMlLeaderboardCandidates,
  updateMlLeaderboardTemplate,
  getMlLeaderboards,
  createMlLeaderboard,
  updateMlLeaderboard,
  deleteMlLeaderboard,
  getMlLeaderboard,
  RESTAPI
} from "api";
import {
  GET_ML_LEADERBOARD_TEMPLATE,
  CREATE_ML_LEADERBOARD_TEMPLATE,
  GET_ML_LEADERBOARD_CANDIDATES,
  UPDATE_ML_LEADERBOARD_TEMPLATE,
  GET_ML_LEADERBOARDS,
  CREATE_ML_LEADERBOARD,
  UPDATE_ML_LEADERBOARD,
  DELETE_ML_LEADERBOARD,
  GET_ML_LEADERBOARD
} from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { checkError, isError } from "utils/api";

const useGetLeaderboardTemplate = (taskId: string) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: leaderboardTemplate } = useApiData(GET_ML_LEADERBOARD_TEMPLATE);

  const { isLoading, isDataReady, shouldInvoke } = useApiState(GET_ML_LEADERBOARD_TEMPLATE, { organizationId, taskId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlLeaderboardTemplate(organizationId, taskId));
    }
  }, [dispatch, organizationId, shouldInvoke, taskId]);

  return {
    isLoading,
    isDataReady,
    leaderboardTemplate
  };
};

const useGetLeaderboardTemplateOnDemand = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading } = useApiState(GET_ML_LEADERBOARD_TEMPLATE);

  const { apiData: leaderboard } = useApiData(GET_ML_LEADERBOARD_TEMPLATE);

  const getData = useCallback(
    (taskId) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(getMlLeaderboardTemplate(organizationId, taskId)).then(() => {
            if (!isError(GET_ML_LEADERBOARD_TEMPLATE, getState())) {
              const apiData = getState()?.[RESTAPI]?.[GET_ML_LEADERBOARD_TEMPLATE];
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

const useCreateLeaderboardTemplate = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_ML_LEADERBOARD_TEMPLATE);

  const onCreate = useCallback(
    (taskId, params) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(createMlLeaderboardTemplate(organizationId, taskId, params)).then(() => {
            if (!isError(CREATE_ML_LEADERBOARD_TEMPLATE, getState())) {
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

const useUpdateLeaderboardTemplate = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(UPDATE_ML_LEADERBOARD_TEMPLATE);

  const onUpdate = useCallback(
    (id, params) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(updateMlLeaderboardTemplate(organizationId, id, params)).then(() => {
            if (!isError(UPDATE_ML_LEADERBOARD_TEMPLATE, getState())) {
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

const useGetLeaderboards = (leaderboardTemplateId: string) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: leaderboards } = useApiData(GET_ML_LEADERBOARDS, []);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_LEADERBOARDS, { organizationId, leaderboardTemplateId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlLeaderboards(organizationId, leaderboardTemplateId));
    }
  }, [dispatch, organizationId, shouldInvoke, leaderboardTemplateId]);

  return {
    isLoading,
    leaderboards
  };
};

const useGetLeaderboardsOnDemand = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: data } = useApiData(GET_ML_LEADERBOARDS, []);

  const { isLoading } = useApiState(GET_ML_LEADERBOARDS);

  const getData = useCallback(
    (leaderboardTemplateId) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(getMlLeaderboards(organizationId, leaderboardTemplateId)).then(() => {
            if (!isError(GET_ML_LEADERBOARDS, getState())) {
              const apiData = getState()?.[RESTAPI]?.[GET_ML_LEADERBOARDS];
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

const useGetLeaderboard = (leaderboardId: string) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: leaderboard } = useApiData(GET_ML_LEADERBOARD);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_LEADERBOARD, { organizationId, leaderboardId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlLeaderboard(organizationId, leaderboardId));
    }
  }, [dispatch, organizationId, shouldInvoke, leaderboardId]);

  return {
    isLoading,
    leaderboard
  };
};

const useGetLeaderboardOnDemand = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: leaderboard } = useApiData(GET_ML_LEADERBOARD);

  const { isLoading } = useApiState(GET_ML_LEADERBOARD);

  const getData = useCallback(
    (leaderboardId) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(getMlLeaderboard(organizationId, leaderboardId)).then(() => {
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

  return {
    isLoading,
    getData,
    data: leaderboard
  };
};

const useCreateLeaderboard = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_ML_LEADERBOARD);

  const onCreate = useCallback(
    (leaderboardTemplateId, params) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(createMlLeaderboard(organizationId, leaderboardTemplateId, params))
            .then(() => checkError(CREATE_ML_LEADERBOARD, getState()))
            .then(() => resolve(getState()[RESTAPI].CREATE_ML_LEADERBOARD))
            .catch(() => reject());
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
    (leaderboardId, params) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(updateMlLeaderboard(organizationId, leaderboardId, params))
            .then(() => checkError(UPDATE_ML_LEADERBOARD, getState()))
            .then(() => resolve(getState()[RESTAPI].GET_ML_LEADERBOARD))
            .catch(() => reject());
        });
      }),
    [dispatch, organizationId]
  );

  return { onUpdate, isLoading };
};

const useDeleteLeaderboard = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(DELETE_ML_LEADERBOARD);

  const onDelete = useCallback(
    (leaderboardId) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(deleteMlLeaderboard(organizationId, leaderboardId)).then(() => {
            if (!isError(DELETE_ML_LEADERBOARD, getState())) {
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

const useGetLeaderboardCandidates = (leaderboardId: string) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: leaderboardCandidates } = useApiData(GET_ML_LEADERBOARD_CANDIDATES, []);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_LEADERBOARD_CANDIDATES, { organizationId, leaderboardId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlLeaderboardCandidates(organizationId, leaderboardId));
    }
  }, [dispatch, organizationId, leaderboardId, shouldInvoke]);

  return {
    isLoading,
    leaderboardCandidates
  };
};

const useGetLeaderboardCandidatesOnDemand = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: leaderboardCandidates } = useApiData(GET_ML_LEADERBOARD_CANDIDATES, []);

  const { isLoading } = useApiState(GET_ML_LEADERBOARD_CANDIDATES);

  const getData = useCallback(
    (leaderboardId) =>
      new Promise((resolve, reject) => {
        dispatch((_, getState) => {
          dispatch(getMlLeaderboardCandidates(organizationId, leaderboardId)).then(() => {
            if (!isError(GET_ML_LEADERBOARD_CANDIDATES, getState())) {
              const apiData = getState()?.[RESTAPI]?.[GET_ML_LEADERBOARD_CANDIDATES];
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
    data: leaderboardCandidates
  };
};

function MlLeaderboardsService() {
  return {
    useGetLeaderboardTemplate,
    useGetLeaderboardTemplateOnDemand,
    useCreateLeaderboardTemplate,
    useUpdateLeaderboardTemplate,

    useGetLeaderboards,
    useGetLeaderboardsOnDemand,

    useGetLeaderboard,
    useGetLeaderboardOnDemand,
    useCreateLeaderboard,
    useUpdateLeaderboard,
    useDeleteLeaderboard,

    useGetLeaderboardCandidates,
    useGetLeaderboardCandidatesOnDemand
  };
}

export default MlLeaderboardsService;

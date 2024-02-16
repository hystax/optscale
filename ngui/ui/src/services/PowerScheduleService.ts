import { useEffect } from "react";
import { useDispatch } from "react-redux";
import {
  getPowerSchedules,
  createPowerSchedule,
  getPowerSchedule,
  deletePowerSchedule,
  updatePowerSchedule,
  attachInstancesToSchedule,
  removeInstancesFromSchedule
} from "api";
import {
  ATTACH_INSTANCES_TO_SCHEDULE,
  CREATE_POWER_SCHEDULES,
  DELETE_POWER_SCHEDULE,
  GET_POWER_SCHEDULE,
  GET_POWER_SCHEDULES,
  REMOVE_INSTANCES_FROM_SCHEDULE,
  UPDATE_POWER_SCHEDULE
} from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

export type PowerScheduleResponse =
  | {
      id: string;
      name: string;
      power_on: string;
      power_off: string;
      timezone: string;
      start_date: number;
      end_date: number;
      last_run: number;
      created_at: number;
      deleted_at: number;
      last_eval: number;
      organization_id: string;
      enabled: boolean;
      last_run_error: string | null;
      resources_count: number;
      resources: object[];
    }
  | Record<string, never>;

export type PowerScheduleApiParams = {
  name: string;
  power_on: string;
  power_off: string;
  timezone: string;
  enabled?: boolean;
  start_date?: number;
  end_date?: number;
};

const useGetAll = (): {
  isLoading: boolean;
  powerSchedules: PowerScheduleResponse[];
} => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { isLoading, shouldInvoke } = useApiState(GET_POWER_SCHEDULES, organizationId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getPowerSchedules(organizationId));
    }
  }, [dispatch, shouldInvoke, organizationId]);

  const {
    apiData: { power_schedules: powerSchedules = [] }
  } = useApiData(GET_POWER_SCHEDULES);

  return {
    isLoading,
    powerSchedules
  };
};

const useCreate = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_POWER_SCHEDULES);

  const onCreate = (params: PowerScheduleApiParams): Promise<void> =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(createPowerSchedule(organizationId, params)).then(() => {
          if (!isError(CREATE_POWER_SCHEDULES, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onCreate, isLoading };
};

const useGet = (
  powerScheduleId: string
): {
  isLoading: boolean;
  powerSchedule: PowerScheduleResponse;
} => {
  const dispatch = useDispatch();

  const { isLoading, shouldInvoke } = useApiState(GET_POWER_SCHEDULE, powerScheduleId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getPowerSchedule(powerScheduleId));
    }
  }, [dispatch, shouldInvoke, powerScheduleId]);

  const { apiData } = useApiData(GET_POWER_SCHEDULE) as { apiData: PowerScheduleResponse };

  return {
    isLoading,
    powerSchedule: apiData
  };
};

const useDelete = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(DELETE_POWER_SCHEDULE);

  const onDelete = (powerScheduleId: string): Promise<void> =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(deletePowerSchedule(powerScheduleId)).then(() => {
          if (!isError(DELETE_POWER_SCHEDULE, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onDelete, isLoading };
};

const useUpdate = () => {
  const dispatch = useDispatch();

  const { isLoading, entityId } = useApiState(UPDATE_POWER_SCHEDULE);

  const onUpdate = (powerScheduleId: string, params: Partial<PowerScheduleApiParams>): Promise<void> =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updatePowerSchedule(powerScheduleId, params)).then(() => {
          if (!isError(UPDATE_POWER_SCHEDULE, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onUpdate, updatingEntityId: entityId, isLoading };
};

const useAttachInstancesToSchedule = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(ATTACH_INSTANCES_TO_SCHEDULE);

  const onAttach = (powerScheduleId: string, instancesToAttach: string[]): Promise<void> =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(attachInstancesToSchedule(powerScheduleId, instancesToAttach)).then(() => {
          if (!isError(ATTACH_INSTANCES_TO_SCHEDULE, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onAttach, isLoading };
};

const useRemoveInstancesFromSchedule = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(REMOVE_INSTANCES_FROM_SCHEDULE);

  const onRemove = (powerScheduleId: string, instancesToRemove: string[]): Promise<void> =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(removeInstancesFromSchedule(powerScheduleId, instancesToRemove)).then(() => {
          if (!isError(REMOVE_INSTANCES_FROM_SCHEDULE, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onRemove, isLoading };
};

function PowerScheduleService() {
  return { useGetAll, useCreate, useGet, useDelete, useUpdate, useAttachInstancesToSchedule, useRemoveInstancesFromSchedule };
}

export default PowerScheduleService;

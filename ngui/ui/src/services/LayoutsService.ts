import { useCallback, useEffect } from "react";
import { useDispatch } from "react-redux";
import { RESTAPI, createLayout, deleteLayout, getLayout, getLayouts, updateLayout } from "api";
import { CREATE_LAYOUT, DELETE_LAYOUT, GET_LAYOUT, GET_LAYOUTS, UPDATE_LAYOUT } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";
import { LAYOUT_TYPES } from "utils/constants";

type LayoutData = {
  id: string;
  name: string;
  data: string;
  type: (typeof LAYOUT_TYPES)[keyof typeof LAYOUT_TYPES];
  shared: boolean;
  owner_id: string;
  entity_id: null | string;
};

const useGetAll = (
  params: {
    layoutType: (typeof LAYOUT_TYPES)[keyof typeof LAYOUT_TYPES];
    entityId?: string;
    includeShared?: boolean;
  },
  onSuccess?: (layout: LayoutData) => void
): {
  isLoading: boolean;
  layouts: LayoutData[];
  currentEmployeeId: string;
} => {
  const dispatch = useDispatch();

  const { layoutType, entityId, includeShared } = params;

  const { organizationId } = useOrganizationInfo();

  const { isLoading, shouldInvoke } = useApiState(GET_LAYOUTS, {
    organizationId,
    layoutType,
    entityId,
    includeShared
  });

  const {
    apiData: { layouts = [], current_employee_id: currentEmployeeId }
  } = useApiData(GET_LAYOUTS);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch((_, getState) => {
        dispatch(getLayouts(organizationId, { layoutType, entityId, includeShared })).then(() => {
          if (!isError(GET_LAYOUTS, getState())) {
            const apiData = getState()[RESTAPI][GET_LAYOUTS];
            if (typeof onSuccess === "function") {
              onSuccess(apiData);
            }
          }
        });
      });
    }
  }, [shouldInvoke, dispatch, organizationId, entityId, includeShared, layoutType, onSuccess]);

  return {
    isLoading,
    layouts,
    currentEmployeeId
  };
};

const useGet = (
  layoutId: string
): {
  isLoading: boolean;
  layout: LayoutData;
} => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading, shouldInvoke } = useApiState(GET_LAYOUT, {
    organizationId,
    layoutId
  });

  const { apiData: layout } = useApiData(GET_LAYOUT);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getLayout(organizationId, layoutId));
    }
  }, [shouldInvoke, dispatch, organizationId, layoutId]);

  return { isLoading, layout };
};

const useGetOneOnDemand = (): {
  isLoading: boolean;
  entityId: string;
  layout: LayoutData;
  onGet: (layoutId: string) => Promise<LayoutData>;
} => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading, entityId } = useApiState(GET_LAYOUT);

  const { apiData: layout } = useApiData(GET_LAYOUT);

  return {
    isLoading,
    entityId,
    layout,
    onGet: useCallback(
      (layoutId) =>
        new Promise((resolve, reject) => {
          dispatch((_, getState) => {
            dispatch(getLayout(organizationId, layoutId)).then(() => {
              if (!isError(GET_LAYOUT, getState())) {
                const apiData = getState()[RESTAPI][GET_LAYOUT];

                return resolve(apiData);
              }
              return reject();
            });
          });
        }),
      [dispatch, organizationId]
    )
  };
};

const useCreate = (): {
  onCreate: (params: {
    name: string;
    data: string;
    type: (typeof LAYOUT_TYPES)[keyof typeof LAYOUT_TYPES];
    shared?: boolean;
    entityId?: string;
  }) => Promise<LayoutData>;
  isLoading: boolean;
} => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_LAYOUT);

  return {
    onCreate: useCallback(
      (params) =>
        new Promise((resolve, reject) => {
          dispatch((_, getState) => {
            dispatch(createLayout(organizationId, params)).then(() => {
              if (!isError(CREATE_LAYOUT, getState())) {
                const apiData = getState()[RESTAPI][CREATE_LAYOUT];
                return resolve(apiData);
              }
              return reject();
            });
          });
        }),
      [dispatch, organizationId]
    ),
    isLoading
  };
};

const useUpdate = (): {
  onUpdate: (id: string, params: { name?: string; data?: string; shared?: boolean }) => Promise<void>;
  isLoading: boolean;
} => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(UPDATE_LAYOUT);

  return {
    onUpdate: useCallback(
      (id, params) =>
        new Promise((resolve, reject) => {
          dispatch((_, getState) => {
            dispatch(updateLayout(organizationId, id, params)).then(() => {
              if (!isError(UPDATE_LAYOUT, getState())) {
                return resolve();
              }
              return reject();
            });
          });
        }),
      [dispatch, organizationId]
    ),
    isLoading
  };
};

const useDelete = (): {
  onDelete: (id: string) => Promise<void>;
  isLoading: boolean;
  entityId: string;
} => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading, entityId } = useApiState(DELETE_LAYOUT);

  return {
    onDelete: useCallback(
      (id) =>
        new Promise((resolve, reject) => {
          dispatch((_, getState) => {
            dispatch(deleteLayout(organizationId, id)).then(() => {
              if (!isError(DELETE_LAYOUT, getState())) {
                return resolve();
              }
              return reject();
            });
          });
        }),
      [dispatch, organizationId]
    ),
    entityId,
    isLoading
  };
};

function LayoutsService() {
  return { useGetAll, useGet, useCreate, useUpdate, useGetOneOnDemand, useDelete };
}

export default LayoutsService;

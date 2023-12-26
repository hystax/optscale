import { useCallback, useEffect } from "react";
import { useDispatch } from "react-redux";
import { RESTAPI, createLayout, deleteLayout, getLayout, getLayouts, updateLayout } from "api";
import { CREATE_LAYOUT, DELETE_LAYOUT, GET_LAYOUT, GET_LAYOUTS, UPDATE_LAYOUT } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

const useGetAll = (params = {}, onSuccess) => {
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

const useGet = (layoutId) => {
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

const useGetOneOnDemand = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading } = useApiState(GET_LAYOUT);

  const { apiData: layout } = useApiData(GET_LAYOUT);

  const onGet = useCallback(
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
  );

  return { isLoading, layout, onGet };
};

const useCreate = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_LAYOUT);

  const onCreate = (params) =>
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
    });

  return { onCreate, isLoading };
};

const useUpdate = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(UPDATE_LAYOUT);

  const onUpdate = (id, params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updateLayout(organizationId, id, params)).then(() => {
          if (!isError(UPDATE_LAYOUT, getState())) {
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
  const { isLoading } = useApiState(DELETE_LAYOUT);

  const onDelete = (id) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(deleteLayout(organizationId, id)).then(() => {
          if (!isError(DELETE_LAYOUT, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onDelete, isLoading };
};

function LayoutsService() {
  return { useGetAll, useGet, useCreate, useUpdate, useGetOneOnDemand, useDelete };
}

export default LayoutsService;

import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { createOrganizationBIExports, deleteBIExport, getBIExport, getOrganizationBIExports, updateBIExport } from "api";
import {
  CREATE_ORGANIZATION_BI_EXPORT,
  DELETE_BI_EXPORT,
  GET_BI_EXPORT,
  GET_ORGANIZATION_BI_EXPORT,
  UPDATE_BI_EXPORT
} from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

export const useGetAll = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { isLoading, shouldInvoke } = useApiState(GET_ORGANIZATION_BI_EXPORT, { organizationId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getOrganizationBIExports(organizationId));
    }
  }, [dispatch, shouldInvoke, organizationId]);

  const {
    apiData: { organization_bis: organizationBIExports = [] }
  } = useApiData(GET_ORGANIZATION_BI_EXPORT);

  return { isLoading, organizationBIExports };
};

const useCreate = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_ORGANIZATION_BI_EXPORT);

  const onCreate = (params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(createOrganizationBIExports(organizationId, params)).then(() => {
          if (!isError(CREATE_ORGANIZATION_BI_EXPORT, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onCreate, isLoading };
};

const useGet = (biExportId) => {
  const dispatch = useDispatch();

  const { isLoading, shouldInvoke } = useApiState(GET_BI_EXPORT, { biExportId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getBIExport(biExportId));
    }
  }, [biExportId, dispatch, shouldInvoke]);

  const { apiData: biExport } = useApiData(GET_BI_EXPORT);

  return { isLoading, biExport };
};

const useUpdate = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(UPDATE_BI_EXPORT);

  const onUpdate = (biExportId, params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updateBIExport(biExportId, params)).then(() => {
          if (!isError(UPDATE_BI_EXPORT, getState())) {
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

  const { isLoading } = useApiState(DELETE_BI_EXPORT);

  const onDelete = (biExportId) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(deleteBIExport(biExportId)).then(() => {
          if (!isError(DELETE_BI_EXPORT, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onDelete, isLoading };
};

function BIExportService() {
  return { useGetAll, useCreate, useUpdate, useGet, useDelete };
}

export default BIExportService;

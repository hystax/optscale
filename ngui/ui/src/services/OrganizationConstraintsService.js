import { useEffect } from "react";
import { useDispatch } from "react-redux";
import {
  createOrganizationConstraint,
  getOrganizationConstraints,
  deleteOrganizationConstraint,
  updateOrganizationConstraint
} from "api";
import { getOrganizationConstraint } from "api/restapi";
import {
  DELETE_ORGANIZATION_CONSTRAINT,
  CREATE_ORGANIZATION_CONSTRAINT,
  GET_ORGANIZATION_CONSTRAINTS,
  GET_ORGANIZATION_CONSTRAINT,
  UPDATE_ORGANIZATION_CONSTRAINT
} from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { checkError } from "utils/api";

export const useGetAll = (types) => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const {
    apiData: { organization_constraints: constraints = [] }
  } = useApiData(GET_ORGANIZATION_CONSTRAINTS);

  const { isLoading, shouldInvoke } = useApiState(GET_ORGANIZATION_CONSTRAINTS, { type: types, organizationId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getOrganizationConstraints(organizationId, { type: types, hit_days: 3 }));
    }
  }, [shouldInvoke, dispatch, organizationId, types]);

  return { isLoading, constraints };
};

const useCreate = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading } = useApiState(CREATE_ORGANIZATION_CONSTRAINT);

  const create = ({ params, onSuccess }) => {
    dispatch((_, getState) => {
      dispatch(createOrganizationConstraint(organizationId, params))
        .then(() => checkError(CREATE_ORGANIZATION_CONSTRAINT, getState()))
        .then(() => {
          if (typeof onSuccess === "function") {
            onSuccess();
          }
        });
    });
  };

  return { create, isLoading };
};

const useGetOne = (constraintId) => {
  const dispatch = useDispatch();
  const { apiData } = useApiData(GET_ORGANIZATION_CONSTRAINT);

  const { isLoading, shouldInvoke } = useApiState(GET_ORGANIZATION_CONSTRAINT, constraintId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getOrganizationConstraint(constraintId));
    }
  }, [shouldInvoke, dispatch, constraintId]);

  return { isLoading, constraint: apiData };
};

const useDelete = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(DELETE_ORGANIZATION_CONSTRAINT);

  return {
    isLoading,
    deleteOrganizationConstraint: ({ id, onSuccess }) => {
      dispatch((_, getState) => {
        dispatch(deleteOrganizationConstraint(id))
          .then(() => checkError(DELETE_ORGANIZATION_CONSTRAINT, getState()))
          .then(() => {
            if (typeof onSuccess === "function") {
              onSuccess();
            }
          });
      });
    }
  };
};

const useUpdate = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(UPDATE_ORGANIZATION_CONSTRAINT);

  return {
    isLoading,
    update: ({ id, params, onSuccess }) => {
      dispatch((_, getState) => {
        dispatch(updateOrganizationConstraint(id, params))
          .then(() => checkError(UPDATE_ORGANIZATION_CONSTRAINT, getState()))
          .then(() => {
            if (typeof onSuccess === "function") {
              onSuccess();
            }
          });
      });
    }
  };
};

function OrganizationConstraintsService() {
  return { useGetAll, useGetOne, useCreate, useDelete, useUpdate };
}

export default OrganizationConstraintsService;

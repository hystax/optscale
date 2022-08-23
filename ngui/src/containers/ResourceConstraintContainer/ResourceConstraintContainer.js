import React from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import {
  createTotalExpenseLimitResourceConstraint,
  createTtlResourceConstraint,
  updateTtlResourceConstraint,
  updateTotalExpenseLimitResourceConstraint,
  deleteResourceConstraint,
  createDailyExpenseLimitResourceConstraint,
  updateDailyExpenseLimitResourceConstraint
} from "api";
import {
  CREATE_TOTAL_EXPENSE_LIMIT_RESOURCE_CONSTRAINT,
  CREATE_TTL_RESOURCE_CONSTRAINT,
  UPDATE_TOTAL_EXPENSE_LIMIT_RESOURCE_CONSTRAINT,
  UPDATE_TTL_RESOURCE_CONSTRAINT,
  DELETE_RESOURCE_CONSTRAINT,
  GET_RESOURCE_LIMIT_HITS,
  CREATE_DAILY_EXPENSE_LIMIT_RESOURCE_CONSTRAINT,
  UPDATE_DAILY_EXPENSE_LIMIT_RESOURCE_CONSTRAINT
} from "api/restapi/actionTypes";
import ResourceConstraintCard from "components/ResourceConstraintCard";
import ResourceConstraintFormPermissionsContainer from "containers/ResourceConstraintFormPermissionsContainer";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";
import { DAILY_EXPENSE_LIMIT, TOTAL_EXPENSE_LIMIT, TTL } from "utils/constraints";

const getApiConfiguration = (type) => {
  switch (type) {
    case TTL:
      return {
        createType: CREATE_TTL_RESOURCE_CONSTRAINT,
        createAction: createTtlResourceConstraint,
        updateType: UPDATE_TTL_RESOURCE_CONSTRAINT,
        updateAction: updateTtlResourceConstraint
      };
    case TOTAL_EXPENSE_LIMIT:
      return {
        createType: CREATE_TOTAL_EXPENSE_LIMIT_RESOURCE_CONSTRAINT,
        createAction: createTotalExpenseLimitResourceConstraint,
        updateType: UPDATE_TOTAL_EXPENSE_LIMIT_RESOURCE_CONSTRAINT,
        updateAction: updateTotalExpenseLimitResourceConstraint
      };
    case DAILY_EXPENSE_LIMIT:
      return {
        createType: CREATE_DAILY_EXPENSE_LIMIT_RESOURCE_CONSTRAINT,
        createAction: createDailyExpenseLimitResourceConstraint,
        updateType: UPDATE_DAILY_EXPENSE_LIMIT_RESOURCE_CONSTRAINT,
        updateAction: updateDailyExpenseLimitResourceConstraint
      };
    default:
      return null;
  }
};

const ResourceConstraintContainer = ({
  resourceId,
  poolId,
  employeeId,
  constraint,
  poolPolicy,
  isGetResourceLoading,
  constraintType
}) => {
  const dispatch = useDispatch();

  const {
    apiData: { limitHits = [] }
  } = useApiData(GET_RESOURCE_LIMIT_HITS);

  const { createType, createAction, updateType, updateAction } = getApiConfiguration(constraintType);

  const { isLoading: createIsLoading } = useApiState(createType);
  const createConstraint = (limit) => dispatch(createAction(resourceId, limit));

  const { isLoading: updateIsLoading } = useApiState(updateType);
  const updateConstraint = ({ limit, policyId }, { onSuccess }) => {
    dispatch((_, getState) => {
      dispatch(updateAction(policyId, limit)).then(() => {
        if (!isError(updateType, getState()) && typeof onSuccess === "function") {
          onSuccess();
        }
      });
    });
  };

  const { isLoading: deleteIsLoading, entityId: deleteEntityId } = useApiState(DELETE_RESOURCE_CONSTRAINT);
  const deleteConstraint = (policyId) => dispatch(deleteResourceConstraint(policyId));

  const limitHit = limitHits
    .filter((hit) => hit.type === constraintType)
    .reduce((result, hit) => {
      if (result.time > hit.time) {
        return result;
      }
      return hit;
    }, {});

  const commonFormProps = {
    poolId,
    updateConstraint,
    createConstraint,
    deleteConstraint,
    constraint,
    constraintType,
    poolPolicy,
    limitHit
  };

  return (
    // If resource is assigned we will need to check if a user has permissions to edit resource's constraints
    <ResourceConstraintFormPermissionsContainer employeeId={employeeId} resourceId={resourceId}>
      {({ isGetPermissionsLoading, canEdit }) => (
        <ResourceConstraintCard
          {...commonFormProps}
          isLoadingProps={{
            isGetDataLoading: isGetResourceLoading || isGetPermissionsLoading,
            isUpdateLoading: updateIsLoading,
            isCreateLoading: createIsLoading,
            isDeleteLoading: constraint?.id === deleteEntityId && deleteIsLoading
          }}
          canEdit={canEdit}
        />
      )}
    </ResourceConstraintFormPermissionsContainer>
  );
};

ResourceConstraintContainer.propTypes = {
  poolId: PropTypes.string,
  resourceId: PropTypes.string,
  constraint: PropTypes.object,
  poolPolicy: PropTypes.object,
  isGetResourceLoading: PropTypes.bool,
  constraintType: PropTypes.string,
  employeeId: PropTypes.string
};

export default ResourceConstraintContainer;

import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { getResource, RESTAPI, getPoolOwners, createAssignmentRule, getAvailablePools } from "api";
import {
  GET_RESOURCE,
  GET_CLOUD_ACCOUNTS,
  CREATE_ASSIGNMENT_RULE,
  GET_POOL_OWNERS,
  GET_AVAILABLE_POOLS
} from "api/restapi/actionTypes";
import AssignmentRuleFormWrapper from "components/AssignmentRuleFormWrapper";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { getResourceUrl } from "urls";
import { isError } from "utils/api";
import {
  TAG_IS,
  CLOUD_IS,
  NAME_ID_IS,
  DEFAULT_CONDITIONS,
  CONDITION,
  CLOUD_IS_CONDITION_VALUE,
  TAG_CONDITION
} from "utils/constants";

const { META_INFO, TYPE } = CONDITION;
const { KEY: TAG_KEY, VALUE: TAG_VALUE } = TAG_CONDITION;

const CreateResourceAssignmentRuleFormContainer = ({ resourceId }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { organizationId, organizationPoolId } = useOrganizationInfo();

  const [isFormDataLoading, setIsFormDataLoading] = useState(false);

  const [defaultValues, setDefaultValues] = useState({
    name: "",
    active: true,
    conditions: DEFAULT_CONDITIONS,
    poolId: "",
    ownerId: ""
  });

  const [pools, setPools] = useState([]);
  const [owners, setOwners] = useState([]);

  const redirect = () => navigate(getResourceUrl(resourceId));

  useEffect(() => {
    dispatch((_, getState) => {
      setIsFormDataLoading(true);
      dispatch(getResource(resourceId, true))
        .then(() => {
          const stateAfterGetResource = getState();
          if (isError(GET_RESOURCE, stateAfterGetResource)) {
            return Promise.reject();
          }

          const {
            resource: { pool_id: resourcePoolId }
          } = stateAfterGetResource?.[RESTAPI]?.[GET_RESOURCE] ?? {};

          return Promise.all([
            dispatch(getAvailablePools(organizationId)),
            dispatch(getPoolOwners(resourcePoolId || organizationPoolId))
          ]);
        })
        .then(() => {
          const stateAfterGetPoolAndOwners = getState();
          if (
            isError(GET_AVAILABLE_POOLS, stateAfterGetPoolAndOwners) ||
            isError(GET_POOL_OWNERS, stateAfterGetPoolAndOwners)
          ) {
            return Promise.reject();
          }
          return Promise.resolve(stateAfterGetPoolAndOwners);
        })
        .then((state) => {
          const {
            resource: {
              name: resourceName,
              pool_id: resourcePoolId,
              employee_id: resourceOwnerId,
              cloud_account_id: cloudAccountId,
              tags = []
            }
          } = state?.[RESTAPI]?.[GET_RESOURCE] ?? {};

          const getConditions = () => {
            const conditions = [];
            // Some resources (clusters) don't belong to any cloud accounts
            if (cloudAccountId) {
              conditions.push({
                [TYPE]: CLOUD_IS,
                [`${META_INFO}_${CLOUD_IS_CONDITION_VALUE}`]: cloudAccountId
              });
            }
            // resource can be unnamed
            if (resourceName) {
              conditions.push({
                [TYPE]: NAME_ID_IS,
                [META_INFO]: resourceName
              });
            }
            return [
              ...conditions,
              ...Object.entries(tags).map(([key, value]) => ({
                [TYPE]: TAG_IS,
                [`${META_INFO}_${TAG_KEY}`]: key,
                [`${META_INFO}_${TAG_VALUE}`]: value
              }))
            ];
          };

          const conditions = getConditions();

          const hasPoolAndOwner = !!(resourcePoolId && resourceOwnerId);

          const { pools: availablePools } = state?.[RESTAPI]?.[GET_AVAILABLE_POOLS] ?? {};

          const { poolOwners = [] } = state?.[RESTAPI]?.[GET_POOL_OWNERS] ?? {};

          let { default_owner_id: defaultOwnerId, id: defaultPoolId } =
            availablePools.find((availablePool) => availablePool.parent_id === null) || {};

          if (hasPoolAndOwner) {
            defaultOwnerId = resourceOwnerId;
            defaultPoolId = resourcePoolId;
          }

          return Promise.resolve({
            defaultValues: {
              conditions,
              poolId: defaultPoolId,
              ownerId: defaultOwnerId
            },
            owners: poolOwners,
            pools: availablePools
          });
        })
        .then((data) => {
          setPools(data.pools);
          setOwners(data.owners);
          setDefaultValues((currentDefaultValues) => ({
            ...currentDefaultValues,
            ...data.defaultValues
          }));
        })
        .catch(() => {})
        .finally(() => setIsFormDataLoading(false));
    });
  }, [dispatch, organizationPoolId, organizationId, resourceId]);

  const { isLoading: isCreateAssignmentRuleLoading } = useApiState(CREATE_ASSIGNMENT_RULE);

  // get cloud accounts
  // Attention: we don't request cloud account here as they are included in the initial loader
  // and we assume that they are up-to-date
  const { apiData: { cloudAccounts = [] } = {} } = useApiData(GET_CLOUD_ACCOUNTS);

  return (
    <AssignmentRuleFormWrapper
      defaultValues={defaultValues}
      pools={pools}
      poolOwners={owners}
      cloudAccounts={cloudAccounts}
      onPoolChange={(newPoolId, callback) => {
        dispatch((_, getState) => {
          dispatch(getPoolOwners(newPoolId)).then(() => {
            const { poolOwners = [] } = getState()?.[RESTAPI]?.[GET_POOL_OWNERS] ?? {};
            setOwners(poolOwners);
            callback(poolOwners);
          });
        });
      }}
      onSubmit={(params) => {
        dispatch((_, getState) => {
          dispatch(createAssignmentRule(organizationId, params)).then(() => {
            if (isError(CREATE_ASSIGNMENT_RULE, getState())) {
              return Promise.reject();
            }
            return redirect();
          });
        });
      }}
      onCancel={redirect}
      readOnlyProps={{
        poolSelector: false,
        ownerSelector: false
      }}
      isLoadingProps={{
        isActionBarLoading: isFormDataLoading,
        isActiveCheckboxLoading: false,
        isNameInputLoading: false,
        isConditionsFieldLoading: isFormDataLoading,
        isPoolSelectorLoading: isFormDataLoading,
        isOwnerSelectorLoading: isFormDataLoading,
        isSubmitButtonLoading: isFormDataLoading || isCreateAssignmentRuleLoading
      }}
    />
  );
};

CreateResourceAssignmentRuleFormContainer.propTypes = {
  resourceId: PropTypes.string.isRequired
};

export default CreateResourceAssignmentRuleFormContainer;

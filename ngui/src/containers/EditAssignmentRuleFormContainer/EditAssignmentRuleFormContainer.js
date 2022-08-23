import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { getPoolOwners, getAvailablePools, getAssignmentRule, updateAssignmentRule, RESTAPI } from "api";
import {
  GET_ASSIGNMENT_RULE,
  UPDATE_ASSIGNMENT_RULE,
  GET_CLOUD_ACCOUNTS,
  GET_POOL_OWNERS,
  GET_AVAILABLE_POOLS
} from "api/restapi/actionTypes";
import AssignmentRuleFormWrapper from "components/AssignmentRuleFormWrapper";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { getPoolUrl, ASSIGNMENT_RULES } from "urls";
import { isError } from "utils/api";
import {
  TAG_IS,
  CLOUD_IS,
  TAG_CONDITION,
  TAG_VALUE_STARTS_WITH,
  CONDITION,
  CLOUD_IS_CONDITION_VALUE,
  TAB_QUERY_PARAM_NAME,
  ORGANIZATION_OVERVIEW_TABS
} from "utils/constants";

const { KEY: TAG_KEY, VALUE: TAG_VALUE } = TAG_CONDITION;
const { META_INFO, TYPE } = CONDITION;

const getConditions = (conditions = []) =>
  conditions.map((condition) => {
    if ([TAG_IS, TAG_VALUE_STARTS_WITH].includes(condition[TYPE])) {
      const { key, value } = JSON.parse(condition[META_INFO]);
      return {
        [`${META_INFO}_${TAG_KEY}`]: key,
        [`${META_INFO}_${TAG_VALUE}`]: value,
        [TYPE]: condition[TYPE]
      };
    }
    if (condition[TYPE] === CLOUD_IS) {
      return {
        [`${META_INFO}_${CLOUD_IS_CONDITION_VALUE}`]: condition[META_INFO],
        [TYPE]: condition[TYPE]
      };
    }
    return {
      [META_INFO]: condition[META_INFO],
      [TYPE]: condition[TYPE]
    };
  });

const EditAssignmentRuleFormContainer = ({ assignmentRuleId, poolId }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { organizationId, organizationPoolId } = useOrganizationInfo();

  const [isFormDataLoading, setIsFormDataLoading] = useState(false);

  const [defaultValues, setDefaultValues] = useState({
    name: "",
    active: false,
    conditions: [],
    poolId: "",
    ownerId: ""
  });

  const redirect = () => {
    if (!poolId) {
      navigate(ASSIGNMENT_RULES);
    } else {
      navigate(`${getPoolUrl(poolId)}?${TAB_QUERY_PARAM_NAME}=${ORGANIZATION_OVERVIEW_TABS.ASSIGNMENT_RULES}`);
    }
  };

  const { isLoading: isUpdateAssignmentRuleLoading } = useApiState(UPDATE_ASSIGNMENT_RULE);

  // Get assignment rule
  const { apiData: { assignmentRule: { name: assignmentRuleName = "" } = {} } = {} } = useApiData(GET_ASSIGNMENT_RULE);

  // Get available pools
  const {
    apiData: { pools = [] }
  } = useApiData(GET_AVAILABLE_POOLS);

  // Get owners
  const {
    apiData: { poolOwners = [] }
  } = useApiData(GET_POOL_OWNERS);

  // get cloud accounts
  // Attention: we don't request cloud account here as they are included in the initial loader
  // and we assume that they are up-to-date
  const { apiData: { cloudAccounts = [] } = {} } = useApiData(GET_CLOUD_ACCOUNTS);

  useEffect(() => {
    dispatch((_, getState) => {
      setIsFormDataLoading(true);

      dispatch(getAssignmentRule(assignmentRuleId))
        .then(() => {
          if (isError(GET_ASSIGNMENT_RULE, getState())) {
            return Promise.reject();
          }
          const {
            assignmentRule: {
              name = "",
              active = false,
              conditions = [],
              pool_id: assignmentRulePoolId = "",
              owner_id: ownerId = ""
            } = {}
          } = getState()?.[RESTAPI]?.[GET_ASSIGNMENT_RULE] ?? {};

          return (
            // Get all available pools
            dispatch(getAvailablePools(organizationId))
              // Get all available owners in the pool for which the assignment rule was created
              .then(() => dispatch(getPoolOwners(assignmentRulePoolId)))
              .then(() => {
                setDefaultValues((currentDefaultValues) => ({
                  ...currentDefaultValues,
                  name,
                  active,
                  conditions: getConditions(conditions),
                  // BE returns 'null' if pool/owner is missing
                  poolId: assignmentRulePoolId ?? "",
                  ownerId: ownerId ?? ""
                }));
              })
          );
        })
        .catch(() => {})
        .finally(() => {
          setIsFormDataLoading(false);
        });
    });
  }, [assignmentRuleId, poolId, dispatch, organizationPoolId, organizationId]);

  return (
    <AssignmentRuleFormWrapper
      defaultValues={defaultValues}
      assignmentRuleName={assignmentRuleName}
      assignmentRuleId={assignmentRuleId}
      pools={pools}
      poolOwners={poolOwners}
      cloudAccounts={cloudAccounts}
      poolId={poolId}
      onPoolChange={(newPoolId, callback) => {
        dispatch((_, getState) => {
          dispatch(getPoolOwners(newPoolId)).then(() => {
            const { poolOwners: owners = [] } = getState()?.[RESTAPI]?.[GET_POOL_OWNERS] ?? {};
            callback(owners);
          });
        });
      }}
      onSubmit={(params) => {
        dispatch((_, getState) => {
          dispatch(updateAssignmentRule(assignmentRuleId, params)).then(() => {
            if (!isError(UPDATE_ASSIGNMENT_RULE, getState())) {
              return redirect();
            }
            return undefined;
          });
        });
      }}
      onCancel={redirect}
      readOnlyProps={{
        poolSelector: !!poolId,
        ownerSelector: false
      }}
      isLoadingProps={{
        isActionBarLoading: isFormDataLoading,
        isActiveCheckboxLoading: isFormDataLoading,
        isNameInputLoading: isFormDataLoading,
        isConditionsFieldLoading: isFormDataLoading,
        isPoolSelectorLoading: isFormDataLoading,
        isOwnerSelectorLoading: isFormDataLoading,
        isSubmitButtonLoading: isFormDataLoading || isUpdateAssignmentRuleLoading
      }}
    />
  );
};

EditAssignmentRuleFormContainer.propTypes = {
  assignmentRuleId: PropTypes.string.isRequired,
  poolId: PropTypes.string
};

export default EditAssignmentRuleFormContainer;

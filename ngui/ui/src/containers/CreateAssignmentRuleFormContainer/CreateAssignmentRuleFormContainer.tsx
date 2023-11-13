import { useEffect, useState } from "react";
import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import { createAssignmentRule, getPoolOwners, RESTAPI, getAvailablePools } from "api";
import { CREATE_ASSIGNMENT_RULE, GET_DATA_SOURCES, GET_POOL_OWNERS, GET_AVAILABLE_POOLS } from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import AssignmentRuleForm from "components/AssignmentRuleForm";
import PageContentWrapper from "components/PageContentWrapper";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { getPoolUrl, ASSIGNMENT_RULES, POOLS } from "urls";
import { isError } from "utils/api";
import { isEmpty as isEmptyArray } from "utils/arrays";
import {
  DEFAULT_CONDITIONS,
  CONDITION,
  TAG_CONDITION,
  CONDITION_TYPES,
  TAG_IS,
  ASSIGNMENT_RULE_CONDITIONS_QUERY_PARAMETER
} from "utils/constants";
import { getQueryParams } from "utils/network";
import { parseJSON } from "utils/strings";

const { META_INFO, TYPE } = CONDITION;
const { KEY: TAG_KEY, VALUE: TAG_VALUE } = TAG_CONDITION;

const PageActionBar = ({ isFormDataLoading, poolId, pools }) => {
  const getActionBarDefinitions = () => {
    if (poolId) {
      const pool = pools.find(({ id }) => id === poolId) ?? {};

      const { name: poolName = "..." } = pool;

      return {
        breadcrumbs: [
          <Link key={1} to={POOLS} component={RouterLink}>
            <FormattedMessage id="pools" />
          </Link>,
          <Link key={2} to={getPoolUrl(poolId)} component={RouterLink}>
            {poolName}
          </Link>
        ],
        titleText: <FormattedMessage id="addAssignmentRuleToTitle" values={{ poolName }} />
      };
    }

    return {
      breadcrumbs: [
        <Link key={1} to={POOLS} component={RouterLink}>
          <FormattedMessage id="pools" />
        </Link>,
        <Link key={2} to={ASSIGNMENT_RULES} component={RouterLink}>
          <FormattedMessage id="assignmentRulesTitle" />
        </Link>
      ],
      titleText: <FormattedMessage id="addAssignmentRuleTitle" />
    };
  };

  const { titleText, breadcrumbs } = getActionBarDefinitions();

  return (
    <ActionBar
      data={{
        breadcrumbs,
        title: {
          text: titleText,
          dataTestId: "lbl_add_rule",
          isLoading: poolId && isFormDataLoading
        }
      }}
    />
  );
};

export const getDefaultConditionsFromQueryParams = (conditionsQueryParam) => {
  const conditions = conditionsQueryParam
    .map((condition) => {
      const parsedCondition = parseJSON(condition, undefined);
      if (parsedCondition) {
        const { type, value } = JSON.parse(condition);

        if (!Object.keys(CONDITION_TYPES).includes(type)) {
          return undefined;
        }

        if (type === TAG_IS) {
          return {
            [TYPE]: type,
            [`${META_INFO}_${TAG_KEY}`]: value?.tagKey,
            [`${META_INFO}_${TAG_VALUE}`]: value?.tagValue
          };
        }
        return {
          [TYPE]: type,
          [META_INFO]: value
        };
      }
      return undefined;
    })
    .filter(Boolean);

  return isEmptyArray(conditions) ? DEFAULT_CONDITIONS : conditions;
};

const CreateAssignmentRuleFormContainer = ({ poolId }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { organizationId, organizationPoolId } = useOrganizationInfo();

  const [isFormDataLoading, setIsFormDataLoading] = useState(false);

  const { [ASSIGNMENT_RULE_CONDITIONS_QUERY_PARAMETER]: conditionsQueryParam } = getQueryParams(true, {
    arrayFormat: "bracket"
  });

  const [defaultValues, setDefaultValues] = useState({
    name: "",
    active: true,
    conditions: conditionsQueryParam ? getDefaultConditionsFromQueryParams(conditionsQueryParam) : DEFAULT_CONDITIONS,
    poolId: "",
    ownerId: ""
  });

  const redirect = () => {
    if (!poolId) {
      navigate(ASSIGNMENT_RULES);
    } else {
      navigate(`${POOLS}?pool=${poolId}`);
    }
  };

  const { isLoading: isCreateAssignmentRuleLoading } = useApiState(CREATE_ASSIGNMENT_RULE);

  // Get available pools
  const {
    apiData: { pools = [] }
  } = useApiData(GET_AVAILABLE_POOLS);

  // Get owners
  const {
    apiData: { poolOwners = [] }
  } = useApiData(GET_POOL_OWNERS);

  useEffect(() => {
    dispatch((_, getState) => {
      setIsFormDataLoading(true);
      dispatch(getAvailablePools(organizationId))
        .then(() => {
          const { pools: availablePools } = getState()?.[RESTAPI]?.[GET_AVAILABLE_POOLS] ?? {};

          // poolId - if creating from a particular pool
          // organizationPoolId - from assignment rules page
          const defaultPoolId = poolId || organizationPoolId;

          const { default_owner_id: defaultOwnerId = "" } =
            availablePools.find((availablePool) => availablePool.id === defaultPoolId) ?? {};

          // There is no need to wait for getPoolOwners to be loaded since the default owner depends only on the pool
          setDefaultValues((currentDefaultValues) => ({
            ...currentDefaultValues,
            poolId: defaultPoolId,
            ownerId: defaultOwnerId
          }));

          return dispatch(getPoolOwners(defaultPoolId));
        })
        .finally(() => setIsFormDataLoading(false));
    });
  }, [poolId, dispatch, organizationPoolId, organizationId]);

  // get cloud accounts
  // Attention: we don't request cloud account here as they are included in the initial loader
  // and we assume that they are up-to-date
  const { apiData: { cloudAccounts = [] } = {} } = useApiData(GET_DATA_SOURCES);

  return (
    <>
      <PageActionBar isFormDataLoading={isFormDataLoading} poolId={poolId} pools={pools} />
      <PageContentWrapper>
        <Box
          sx={{
            width: { md: "50%" }
          }}
        >
          <AssignmentRuleForm
            onSubmit={(params) => {
              dispatch((_, getState) => {
                dispatch(createAssignmentRule(organizationId, params)).then(() => {
                  if (!isError(CREATE_ASSIGNMENT_RULE, getState())) {
                    redirect();
                  }
                  return undefined;
                });
              });
            }}
            onCancel={redirect}
            pools={pools}
            cloudAccounts={cloudAccounts}
            onPoolChange={(newPoolId, callback) => {
              dispatch((_, getState) => {
                dispatch(getPoolOwners(newPoolId)).then(() => {
                  const { poolOwners: owners = [] } = getState()?.[RESTAPI]?.[GET_POOL_OWNERS] ?? {};
                  callback(owners);
                });
              });
            }}
            poolOwners={poolOwners}
            defaultValues={defaultValues}
            readOnlyProps={{
              poolSelector: !!poolId,
              ownerSelector: false
            }}
            isLoadingProps={{
              isActiveCheckboxLoading: false,
              isNameInputLoading: false,
              isConditionsFieldLoading: false,
              isPoolSelectorLoading: isFormDataLoading,
              isOwnerSelectorLoading: isFormDataLoading,
              isSubmitButtonLoading: isFormDataLoading || isCreateAssignmentRuleLoading
            }}
          />
        </Box>
      </PageContentWrapper>
    </>
  );
};

export default CreateAssignmentRuleFormContainer;

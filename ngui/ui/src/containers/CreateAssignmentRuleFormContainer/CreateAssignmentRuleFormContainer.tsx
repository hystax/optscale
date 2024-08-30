import { useEffect, useState } from "react";
import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import { createAssignmentRule, getPoolOwners, RESTAPI, getAvailablePools } from "api";
import { CREATE_ASSIGNMENT_RULE, GET_DATA_SOURCES, GET_POOL_OWNERS, GET_AVAILABLE_POOLS } from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import AssignmentRuleForm from "components/forms/AssignmentRuleForm";
import { FIELD_NAMES } from "components/forms/AssignmentRuleForm/utils";
import PageContentWrapper from "components/PageContentWrapper";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { ASSIGNMENT_RULES, POOLS } from "urls";
import { isError } from "utils/api";
import { isEmpty as isEmptyArray } from "utils/arrays";
import {
  DEFAULT_CONDITIONS,
  CONDITION_TYPES,
  TAG_IS,
  ASSIGNMENT_RULE_CONDITIONS_QUERY_PARAMETER,
  CLOUD_IS,
  TAG_VALUE_STARTS_WITH
} from "utils/constants";
import { getQueryParams } from "utils/network";
import { parseJSON } from "utils/strings";

const PageActionBar = ({ isFormDataLoading }) => {
  const getActionBarDefinitions = () => ({
    breadcrumbs: [
      <Link key={1} to={POOLS} component={RouterLink}>
        <FormattedMessage id="pools" />
      </Link>,
      <Link key={2} to={ASSIGNMENT_RULES} component={RouterLink}>
        <FormattedMessage id="assignmentRulesTitle" />
      </Link>
    ],
    titleText: <FormattedMessage id="addAssignmentRuleTitle" />
  });

  const { titleText, breadcrumbs } = getActionBarDefinitions();

  return (
    <ActionBar
      data={{
        breadcrumbs,
        title: {
          text: titleText,
          dataTestId: "lbl_add_rule",
          isLoading: isFormDataLoading
        }
      }}
    />
  );
};

const getDefaultConditionsFromQueryParams = (conditionsQueryParam) => {
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
            [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.TYPE]: type,
            [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.TAG_KEY_FIELD_NAME]: value?.tagKey,
            [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.TAG_VALUE_FIELD_NAME]: value?.tagValue
          };
        }

        if (type === TAG_VALUE_STARTS_WITH) {
          return {
            [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.TYPE]: type,
            [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.TAG_KEY_FIELD_NAME]: value?.tagKey,
            [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.TAG_VALUE_FIELD_NAME]: value?.tagValue
          };
        }

        if (type === CLOUD_IS) {
          return {
            [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.TYPE]: type,
            [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.CLOUD_IS_FIELD_NAME]: value
          };
        }

        return {
          [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.TYPE]: type,
          [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.META_INFO]: value
        };
      }
      return undefined;
    })
    .filter(Boolean);

  return isEmptyArray(conditions) ? DEFAULT_CONDITIONS : conditions;
};

const CreateAssignmentRuleFormContainer = () => {
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
    navigate(ASSIGNMENT_RULES);
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

          const { default_owner_id: defaultOwnerId = "" } =
            availablePools.find((availablePool) => availablePool.id === organizationPoolId) ?? {};

          // There is no need to wait for getPoolOwners to be loaded since the default owner depends only on the pool
          setDefaultValues((currentDefaultValues) => ({
            ...currentDefaultValues,
            poolId: organizationPoolId,
            ownerId: defaultOwnerId
          }));

          return dispatch(getPoolOwners(organizationPoolId));
        })
        .finally(() => setIsFormDataLoading(false));
    });
  }, [dispatch, organizationPoolId, organizationId]);

  // get cloud accounts
  // Attention: we don't request cloud account here as they are included in the initial loader
  // and we assume that they are up-to-date
  const { apiData: { cloudAccounts = [] } = {} } = useApiData(GET_DATA_SOURCES);

  return (
    <>
      <PageActionBar isFormDataLoading={isFormDataLoading} pools={pools} />
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

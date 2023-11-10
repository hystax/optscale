import { useEffect, useState } from "react";
import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import { getPoolOwners, getAvailablePools, getAssignmentRule, updateAssignmentRule, RESTAPI } from "api";
import {
  GET_ASSIGNMENT_RULE,
  UPDATE_ASSIGNMENT_RULE,
  GET_DATA_SOURCES,
  GET_POOL_OWNERS,
  GET_AVAILABLE_POOLS
} from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import AssignmentRuleForm from "components/AssignmentRuleForm";
import PageContentWrapper from "components/PageContentWrapper";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { ASSIGNMENT_RULES, POOLS } from "urls";
import { isError } from "utils/api";
import { TAG_IS, CLOUD_IS, TAG_CONDITION, TAG_VALUE_STARTS_WITH, CONDITION, CLOUD_IS_CONDITION_VALUE } from "utils/constants";

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
      navigate(`${POOLS}?pool=${poolId}`);
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
  const { apiData: { cloudAccounts = [] } = {} } = useApiData(GET_DATA_SOURCES);

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
    <>
      <ActionBar
        data={{
          breadcrumbs: [
            <Link key={1} to={POOLS} component={RouterLink}>
              <FormattedMessage id="pools" />
            </Link>,
            <Link key={2} to={ASSIGNMENT_RULES} component={RouterLink}>
              <FormattedMessage id="assignmentRules" />
            </Link>
          ],
          title: {
            text: <FormattedMessage id="edit{}" values={{ value: assignmentRuleName }} />,
            dataTestId: "lbl_edit_rule",
            isLoading: isFormDataLoading
          }
        }}
      />
      <PageContentWrapper>
        <Box
          sx={{
            width: { md: "50%" }
          }}
        >
          <AssignmentRuleForm
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
            pools={pools}
            cloudAccounts={cloudAccounts}
            isEdit
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
              isActiveCheckboxLoading: isFormDataLoading,
              isNameInputLoading: isFormDataLoading,
              isConditionsFieldLoading: isFormDataLoading,
              isPoolSelectorLoading: isFormDataLoading,
              isOwnerSelectorLoading: isFormDataLoading,
              isSubmitButtonLoading: isFormDataLoading || isUpdateAssignmentRuleLoading
            }}
          />
        </Box>
      </PageContentWrapper>
    </>
  );
};

export default EditAssignmentRuleFormContainer;

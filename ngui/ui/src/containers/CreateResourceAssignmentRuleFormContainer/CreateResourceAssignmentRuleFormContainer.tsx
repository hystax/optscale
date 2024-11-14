import { useState, useEffect } from "react";
import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import { getResource, RESTAPI, getPoolOwners, createAssignmentRule, getAvailablePools } from "api";
import {
  GET_RESOURCE,
  GET_DATA_SOURCES,
  CREATE_ASSIGNMENT_RULE,
  GET_POOL_OWNERS,
  GET_AVAILABLE_POOLS
} from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import ActionBarResourceNameTitleText from "components/ActionBarResourceNameTitleText";
import AssignmentRuleForm from "components/forms/AssignmentRuleForm";
import { FIELD_NAMES } from "components/forms/AssignmentRuleForm/utils";
import PageContentWrapper from "components/PageContentWrapper";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useAssignmentRulesAvailableFilters } from "hooks/useAssignmentRulesAvailableFilters";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { RESOURCES, getResourceUrl } from "urls";
import { isError } from "utils/api";
import { TAG_IS, CLOUD_IS, NAME_ID_IS, DEFAULT_CONDITIONS, RESOURCE_TYPE_IS, REGION_IS } from "utils/constants";
import { getResourceDisplayedName } from "utils/resources";

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
  const [resource, setResource] = useState({});

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
          const { resource: loadedResource } = state?.[RESTAPI]?.[GET_RESOURCE] ?? {};

          const {
            name: resourceName,
            pool_id: resourcePoolId,
            employee_id: resourceOwnerId,
            cloud_account_id: cloudAccountId,
            tags = [],
            resource_type: resourceType,
            region
          } = loadedResource;

          const getConditions = () => {
            const conditions = [];
            // Some resources (clusters) don't belong to any cloud accounts
            if (cloudAccountId) {
              conditions.push({
                [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.TYPE]: CLOUD_IS,
                [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.CLOUD_IS_FIELD_NAME]: cloudAccountId
              });
            }
            // resource can be unnamed
            if (resourceName) {
              conditions.push({
                [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.TYPE]: NAME_ID_IS,
                [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.META_INFO]: resourceName
              });
            }

            // Environment resources have no region
            if (region) {
              conditions.push({
                [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.TYPE]: REGION_IS,
                [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.REGION_IS_FIELD_NAME]: region
              });
            }

            return [
              ...conditions,
              {
                [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.TYPE]: RESOURCE_TYPE_IS,
                [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.RESOURCE_TYPE_IS_FIELD_NAME]: resourceType
              },
              ...Object.entries(tags).map(([key, value]) => ({
                [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.TYPE]: TAG_IS,
                [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.TAG_KEY_FIELD_NAME]: key,
                [FIELD_NAMES.CONDITIONS_FIELD_ARRAY.TAG_VALUE_FIELD_NAME]: value
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
            pools: availablePools,
            resource: loadedResource
          });
        })
        .then((data) => {
          setPools(data.pools);
          setOwners(data.owners);
          setResource(data.resource);
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
  const { apiData: { cloudAccounts = [] } = {} } = useApiData(GET_DATA_SOURCES);

  const { isLoading: isAvailableFiltersLoading, resourceTypes, regions } = useAssignmentRulesAvailableFilters();

  return (
    <>
      <ActionBar
        data={{
          breadcrumbs: [
            <Link key={1} to={RESOURCES} component={RouterLink}>
              <FormattedMessage id="resources" />
            </Link>,
            <Link key={2} to={getResourceUrl(resource.id)} component={RouterLink}>
              <ActionBarResourceNameTitleText resourceName={getResourceDisplayedName(resource)} />
            </Link>
          ],
          title: {
            text: <FormattedMessage id="addAssignmentRuleTitle" />,
            dataTestId: "lbl_add_rule",
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
                dispatch(createAssignmentRule(organizationId, params)).then(() => {
                  if (isError(CREATE_ASSIGNMENT_RULE, getState())) {
                    return Promise.reject();
                  }
                  return redirect();
                });
              });
            }}
            onCancel={redirect}
            pools={pools}
            cloudAccounts={cloudAccounts}
            resourceTypes={resourceTypes}
            regions={regions}
            onPoolChange={(newPoolId, callback) => {
              dispatch((_, getState) => {
                dispatch(getPoolOwners(newPoolId)).then(() => {
                  const { poolOwners = [] } = getState()?.[RESTAPI]?.[GET_POOL_OWNERS] ?? {};
                  setOwners(poolOwners);
                  callback(poolOwners);
                });
              });
            }}
            poolOwners={owners}
            defaultValues={defaultValues}
            isLoadingProps={{
              isActiveCheckboxLoading: false,
              isNameInputLoading: false,
              isConditionsFieldLoading: isFormDataLoading || isAvailableFiltersLoading,
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

export default CreateResourceAssignmentRuleFormContainer;

import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { getTtlAnalysis, getAvailablePools } from "api";
import { API } from "api/reducer";
import { GET_TTL_ANALYSIS, GET_AVAILABLE_POOLS } from "api/restapi/actionTypes";
import SnackbarAlert from "components/SnackbarAlert";
import TtlAnalysis from "components/TtlAnalysis";
import { setDate } from "containers/RangePickerFormContainer/actionCreators";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useInitialMount } from "hooks/useInitialMount";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { useRootData } from "hooks/useRootData";
import { isError, isTtlExpired } from "utils/api";
import {
  TTL_MODES,
  TTL_ANALYSIS_QUERY_PARAMETERS,
  TTL_ANALYSIS_TOP_SECTION_TYPES,
  START_DATE_PICKER_NAME,
  END_DATE_PICKER_NAME,
  DATE_RANGE_TYPE
} from "utils/constants";
import { getQueryParams, updateQueryParams } from "utils/network";

const { PREDEFINED_TTL, CUSTOM_TTL } = TTL_MODES;

const findPool = (id, pools) => pools.find((b) => b.id === id);

const getTtlPolicyLimit = (pool) => pool?.policies?.find((p) => p.type === "ttl")?.limit ?? "";

const isTtlQueryParameterValueValid = (value) => Number.isInteger(value) && value >= 1;

const getDefaultCustomTtlValue = (ttlLimit) => {
  const ttlQueryParameter = Number(getQueryParams().ttl);
  return String(isTtlQueryParameterValueValid(ttlQueryParameter) ? ttlQueryParameter : ttlLimit);
};

const POOL_ID = "poolId";
const TTL_MODE = "ttlMode";

const TtlAnalysisContainer = ({ pathPoolId }) => {
  const dispatch = useDispatch();
  const { organizationId, organizationPoolId } = useOrganizationInfo();

  const isPoolIdPredefined = !!pathPoolId;

  const poolId = isPoolIdPredefined ? pathPoolId : organizationPoolId;

  const { isLoading: isGetAvailablePoolsLoading, shouldInvoke: shouldInvokeGetAvailablePools } = useApiState(
    GET_AVAILABLE_POOLS,
    { organizationId }
  );

  const { rootData: getAvailablePoolsApiTimestamp } = useRootData(API, (result) => result?.[GET_AVAILABLE_POOLS]?.timestamp);

  const { isLoading: isGetTtlAnalysisLoading } = useApiState(GET_TTL_ANALYSIS);

  const [alertState, setAlertState] = useState({
    show: false,
    message: null
  });

  const [shouldRenderReportLayout, setShouldRenderReportLayout] = useState(false);

  const [topSectionComponent, setTopSectionComponent] = useState({
    type: TTL_ANALYSIS_TOP_SECTION_TYPES.FORM
  });

  const [defaultValues, setDefaultValues] = useState({});

  const {
    apiData: { pools: allPools = [] }
  } = useApiData(GET_AVAILABLE_POOLS);

  const { isInitialMount, setIsInitialMount } = useInitialMount();

  const {
    apiData: {
      resources_tracked: resourcesTracked,
      resources_outside_of_ttl: resourcesOutsideOfTtl,
      total_expenses: totalExpenses,
      expenses_outside_of_ttl: expensesOutsideOfTtl,
      resources = []
    } = {}
  } = useApiData(GET_TTL_ANALYSIS);

  useEffect(() => {
    if (shouldInvokeGetAvailablePools && isInitialMount) {
      setIsInitialMount(false);
      dispatch(getAvailablePools(organizationId));
    }
  }, [dispatch, isInitialMount, organizationId, setIsInitialMount, shouldInvokeGetAvailablePools]);

  useEffect(() => {
    const updateDefaultValues = () => {
      const shouldUsePoolQueryParameter = !isPoolIdPredefined;
      const { [TTL_ANALYSIS_QUERY_PARAMETERS.POOL_ID]: poolIdQueryParams, [TTL_ANALYSIS_QUERY_PARAMETERS.TTL]: ttl } =
        getQueryParams();
      const ttlValue = Number(ttl);

      if (poolIdQueryParams && shouldUsePoolQueryParameter) {
        const queryParamPool = findPool(poolIdQueryParams, allPools);
        if (queryParamPool) {
          const ttlPolicyLimit = getTtlPolicyLimit(queryParamPool);
          setDefaultValues({
            [POOL_ID]: poolIdQueryParams,
            [CUSTOM_TTL]: getDefaultCustomTtlValue(getTtlPolicyLimit(queryParamPool)),
            [TTL_MODE]: isTtlQueryParameterValueValid(ttlValue) || !ttlPolicyLimit ? CUSTOM_TTL : PREDEFINED_TTL
          });
        } else {
          setDefaultValues({
            [POOL_ID]: "",
            [CUSTOM_TTL]: getDefaultCustomTtlValue(""),
            [TTL_MODE]: CUSTOM_TTL
          });
        }
      } else {
        const organizationPool = findPool(poolId, allPools);
        const ttlPolicyLimit = getTtlPolicyLimit(organizationPool);
        setDefaultValues({
          [POOL_ID]: poolId,
          [CUSTOM_TTL]: getDefaultCustomTtlValue(ttlPolicyLimit),
          [TTL_MODE]: isTtlQueryParameterValueValid(ttlValue) || !ttlPolicyLimit ? CUSTOM_TTL : PREDEFINED_TTL
        });
      }
    };

    const validatePool = () => {
      const shouldUsePoolQueryParameter = !isPoolIdPredefined;
      const { [TTL_ANALYSIS_QUERY_PARAMETERS.POOL_ID]: poolIdQueryParams } = getQueryParams();

      if (poolIdQueryParams && shouldUsePoolQueryParameter) {
        const queryParamPool = findPool(poolIdQueryParams, allPools);
        if (!queryParamPool) {
          setAlertState({
            show: true,
            message: <FormattedMessage id="poolIsNotFoundSelectManually" values={{ id: poolIdQueryParams }} />
          });
        }
      }
    };

    validatePool();
    updateDefaultValues();
  }, [allPools, poolId, isPoolIdPredefined]);

  const onTtlAnalysisFormSubmit = ({
    poolId: id,
    poolName,
    poolType,
    ttl,
    customTtl,
    startDateTimestamp,
    endDateTimestamp,
    ttlMode
  }) => {
    if (!shouldRenderReportLayout) {
      setShouldRenderReportLayout(true);
    }
    const startDate = startDateTimestamp;
    const endDate = endDateTimestamp;
    updateQueryParams({
      [TTL_ANALYSIS_QUERY_PARAMETERS.POOL_ID]: pathPoolId ? undefined : id,
      [TTL_ANALYSIS_QUERY_PARAMETERS.TTL]: ttlMode === TTL_MODES.CUSTOM_TTL ? ttl : undefined,
      startDate,
      endDate
    });
    dispatch(setDate(startDate, endDate, DATE_RANGE_TYPE.TTL_ANALYSIS));
    setDefaultValues((values) => ({
      ...values,
      [POOL_ID]: id,
      [TTL_MODE]: ttlMode,
      [CUSTOM_TTL]: customTtl
    }));
    dispatch((_, getState) => {
      dispatch(
        getTtlAnalysis(id, {
          startDate,
          endDate,
          ttl
        })
      ).then(() => {
        if (isError(GET_TTL_ANALYSIS, getState())) {
          setShouldRenderReportLayout(false);
          setTopSectionComponent({
            type: TTL_ANALYSIS_TOP_SECTION_TYPES.FORM
          });
        } else {
          setTopSectionComponent({
            type: TTL_ANALYSIS_TOP_SECTION_TYPES.APPLIED_FILTERS,
            payload: {
              poolId: id,
              poolName,
              poolType,
              ttl,
              startDate,
              endDate
            }
          });
        }
      });
    });
  };

  const onEdit = () => {
    if (isTtlExpired(getAvailablePoolsApiTimestamp)) {
      dispatch(getAvailablePools(organizationId));
    }
    setTopSectionComponent({ type: TTL_ANALYSIS_TOP_SECTION_TYPES.FORM });
  };

  return (
    <>
      <SnackbarAlert
        body={alertState.message}
        openState={alertState.show}
        severity="error"
        handleClose={() => setAlertState((st) => ({ ...st, show: false }))}
      />
      <TtlAnalysis
        topSectionComponent={topSectionComponent}
        setTopSectionComponent={setTopSectionComponent}
        shouldRenderReportLayout={shouldRenderReportLayout}
        onEdit={onEdit}
        TtlAnalysisFormProps={{
          isLoading: isGetAvailablePoolsLoading,
          isPoolSelectorReadOnly: isPoolIdPredefined,
          onSubmit: onTtlAnalysisFormSubmit,
          pools: allPools,
          defaultValues,
          fieldNames: {
            poolFieldName: POOL_ID,
            ttlModeFieldName: TTL_MODE,
            customTtlFieldName: CUSTOM_TTL,
            startDateFieldName: START_DATE_PICKER_NAME,
            endDateFieldName: END_DATE_PICKER_NAME
          }
        }}
        TtlAnalysisReportProps={{
          resourcesTracked,
          resourcesOutsideOfTtl,
          totalExpenses,
          expensesOutsideOfTtl,
          resources,
          isLoading: isGetTtlAnalysisLoading
        }}
      />
    </>
  );
};

TtlAnalysisContainer.propTypes = {
  pathPoolId: PropTypes.string
};

export default TtlAnalysisContainer;

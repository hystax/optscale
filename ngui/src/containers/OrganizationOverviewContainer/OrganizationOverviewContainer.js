import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { getPool, getPoolAllowedActions, RESTAPI } from "api";
import { GET_POOL_ALLOWED_ACTIONS } from "api/auth/actionTypes";
import { GET_POOL } from "api/restapi/actionTypes";
import { MESSAGE_TYPES } from "components/ContentBackdrop";
import Mocked from "components/Mocked";
import OrganizationOverview, { OrganizationOverviewMocked } from "components/OrganizationOverview";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";
import { isEmpty } from "utils/arrays";

const withPoolChildren = true;
const withPoolDetails = true;

const OrganizationOverviewContainer = ({ poolId }) => {
  const dispatch = useDispatch();

  const {
    apiData: { pool = {} }
  } = useApiData(GET_POOL);

  // TODO - details: true is temporary, remove it and fix the root cause NGUI-1055
  const {
    isLoading: isGetPoolLoading,
    shouldInvoke: shouldInvokeGetPool,
    isDataReady: isGetPoolDataReady
  } = useApiState(GET_POOL, {
    poolId,
    children: withPoolChildren,
    details: withPoolDetails
  });
  const { isLoading: isGetPoolAllowedActionsLoading } = useApiState(GET_POOL_ALLOWED_ACTIONS);

  useEffect(() => {
    dispatch((_, getState) => {
      if (shouldInvokeGetPool) {
        dispatch(getPool(poolId, withPoolChildren, withPoolDetails)).then(() => {
          if (!isError(GET_POOL, getState())) {
            const { pool: { id, children = [] } = {} } = getState()?.[RESTAPI]?.[GET_POOL] ?? {};

            const poolIds = children.map((child) => child.id);
            poolIds.push(id);

            dispatch(getPoolAllowedActions(poolIds));
          }
        });
      }
    });
  }, [dispatch, poolId, shouldInvokeGetPool]);

  return (
    <Mocked
      mock={<OrganizationOverviewMocked id={poolId} />}
      backdropMessageType={MESSAGE_TYPES.POOLS}
      mockCondition={pool.limit === 0 && pool.parent_id === null && isEmpty(pool.children)}
    >
      <OrganizationOverview
        pool={pool}
        isLoadingProps={{ isGetPoolLoading, isGetPoolAllowedActionsLoading, isGetPoolDataReady }}
      />
    </Mocked>
  );
};

OrganizationOverviewContainer.propTypes = {
  poolId: PropTypes.string.isRequired
};

export default OrganizationOverviewContainer;

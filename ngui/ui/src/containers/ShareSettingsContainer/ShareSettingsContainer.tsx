import { useState } from "react";
import { useDispatch } from "react-redux";
import { createExpensesExport, deleteExpensesExport, RESTAPI } from "api";
import { CREATE_POOL_EXPENSES_EXPORT, DELETE_POOL_EXPENSES_EXPORT, UPDATE_POOL_EXPENSES_EXPORT } from "api/restapi/actionTypes";
import ShareSettings from "components/ShareSettings";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useApiState } from "hooks/useApiState";
import { SCOPE_TYPES } from "utils/constants";

const ShareSettingsContainer = ({ poolId, poolName, poolPurpose, initialLink }) => {
  const dispatch = useDispatch();

  const [currentLink, setCurrentLink] = useState(initialLink || "");

  const canEdit = useIsAllowed({ entityType: SCOPE_TYPES.POOL, entityId: poolId, requiredActions: ["MANAGE_POOLS"] });

  const { isLoading: createLinkIsLoading } = useApiState(CREATE_POOL_EXPENSES_EXPORT, poolId);
  const { isLoading: deleteLinkIsLoading } = useApiState(DELETE_POOL_EXPENSES_EXPORT, poolId);

  const switchClickHandler = (value) => {
    dispatch((_, getState) => {
      if (value) {
        dispatch(createExpensesExport(poolId)).then(() => {
          setCurrentLink(getState()?.[RESTAPI]?.[UPDATE_POOL_EXPENSES_EXPORT]?.expenses_export_link || "");
        });
      } else {
        dispatch(deleteExpensesExport(poolId)).then(() => {
          setCurrentLink("");
        });
      }
    });
  };

  return (
    <ShareSettings
      canEdit={canEdit}
      currentLink={currentLink}
      onChange={switchClickHandler}
      poolName={poolName}
      poolPurpose={poolPurpose}
      isLoading={createLinkIsLoading || deleteLinkIsLoading}
    />
  );
};

export default ShareSettingsContainer;

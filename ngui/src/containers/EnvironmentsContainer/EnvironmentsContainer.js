import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import { updateEnvironmentActivity } from "api";
import { UPDATE_ENVIRONMENT_ACTIVITY } from "api/restapi/actionTypes";
import { MESSAGE_TYPES } from "components/ContentBackdrop";
import Environments, { EnvironmentsMocked } from "components/Environments";
import Mocked from "components/Mocked";
import { ENVIRONMENTS_TOUR, TOURS, startTour } from "components/ProductTour";
import { useApiState } from "hooks/useApiState";
import { useRootData } from "hooks/useRootData";
import EnvironmentsService from "services/EnvironmentsService";
import { isEmpty } from "utils/arrays";

const EnvironmentsContainer = () => {
  const { useGet } = EnvironmentsService();
  const dispatch = useDispatch();

  const {
    rootData: { [ENVIRONMENTS_TOUR]: { isOpen, isFinished } = {} }
  } = useRootData(TOURS);

  useEffect(() => {
    if (!isOpen && !isFinished) {
      dispatch(startTour(ENVIRONMENTS_TOUR));
    }
  }, [dispatch, isFinished, isOpen]);

  const startEnvironmentsTour = () => {
    dispatch(startTour(ENVIRONMENTS_TOUR));
  };

  const { isGetEnvironmentsLoading, isGetResourceAllowedActionsLoading, environments } = useGet();

  const { isLoading: isUpdateEnvironmentLoading, entityId } = useApiState(UPDATE_ENVIRONMENT_ACTIVITY);

  // TODO: improve loading, currently we need to reset these APIs in order to update activity and activity action icon
  // Idea: show full table loading state on initial load (see FinOps approach)
  const updateActivity = (environmentId, isActive) => {
    dispatch(updateEnvironmentActivity(environmentId, { active: isActive }));
  };

  return (
    <Mocked
      mock={<EnvironmentsMocked />}
      mockCondition={(!isGetEnvironmentsLoading && isEmpty(environments)) || isOpen}
      backdropMessageType={MESSAGE_TYPES.ENVIRONMENTS}
    >
      <Environments
        isLoadingProps={{ isGetEnvironmentsLoading, isUpdateEnvironmentLoading, isGetResourceAllowedActionsLoading }}
        environments={environments}
        entityId={entityId}
        onUpdateActivity={updateActivity}
        startEnvironmentsTour={startEnvironmentsTour}
      />
    </Mocked>
  );
};

export default EnvironmentsContainer;

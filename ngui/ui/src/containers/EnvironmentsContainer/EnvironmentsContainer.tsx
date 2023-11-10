import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { updateEnvironmentActivity } from "api";
import { UPDATE_ENVIRONMENT_ACTIVITY } from "api/restapi/actionTypes";
import Environments, { EnvironmentsMocked } from "components/Environments";
import Mocked, { MESSAGE_TYPES } from "components/Mocked";
import { useStartTour, ENVIRONMENTS_TOUR, TOURS } from "components/Tour";
import { useApiState } from "hooks/useApiState";
import { useIsDownMediaQuery } from "hooks/useMediaQueries";
import { useRootData } from "hooks/useRootData";
import EnvironmentsService from "services/EnvironmentsService";
import { isEmpty } from "utils/arrays";

const EnvironmentsContainer = () => {
  const startTour = useStartTour();

  const { useGet } = EnvironmentsService();
  const dispatch = useDispatch();

  const {
    rootData: { [ENVIRONMENTS_TOUR]: { isOpen, isFinished } = {} }
  } = useRootData(TOURS);

  const isMobile = useIsDownMediaQuery("sm");

  // opens tour on first page visit
  useEffect(() => {
    if (!isOpen && !isFinished && !isMobile) {
      startTour(ENVIRONMENTS_TOUR);
    }
  }, [startTour, isFinished, isOpen, isMobile]);

  const startEnvironmentsTour = () => {
    startTour(ENVIRONMENTS_TOUR);
  };

  const { isGetEnvironmentsLoading, isGetResourceAllowedActionsLoading, environments } = useGet();

  const { isLoading: isUpdateEnvironmentLoading, entityId } = useApiState(UPDATE_ENVIRONMENT_ACTIVITY);

  // TODO: improve loading, currently we need to reset these APIs in order to update activity and activity action icon
  // Idea: show full table loading state on initial load (see FinOps approach)
  const updateActivity = (environmentId, isActive) => {
    dispatch(updateEnvironmentActivity(environmentId, isActive));
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

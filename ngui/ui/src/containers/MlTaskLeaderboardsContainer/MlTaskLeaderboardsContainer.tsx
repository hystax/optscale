import { useCallback, useEffect } from "react";
import { useDispatch } from "react-redux";
import { useParams } from "react-router-dom";
import { GET_ML_LEADERBOARD_TEMPLATE } from "api/restapi/actionTypes";
import MlTaskLeaderboards from "components/MlTaskLeaderboards";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import {
  getStoreLeaderboardId,
  setStoreLeaderboardId,
  useTaskSelectedLeaderboardId
} from "reducers/taskBreakdown/useTaskSelectedLeaderboardId";
import MlLeaderboardsService from "services/MlLeaderboardsService";
import { isEmpty as isEmptyArray } from "utils/arrays";

const MlTaskLeaderboardsContainer = ({ task }) => {
  const { taskId } = useParams() as { taskId: string };
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const {
    useGetLeaderboardTemplateOnDemand,
    useGetLeaderboardsOnDemand,
    useGetLeaderboardOnDemand,
    useGetLeaderboardCandidatesOnDemand
  } = MlLeaderboardsService();

  const {
    isLoading: isGetLeaderboardTemplateLoading,
    data: leaderboardTemplate,
    getData: getLeaderboardTemplate
  } = useGetLeaderboardTemplateOnDemand();

  const { isLoading: isGetLeaderboardsLoading, data: leaderboards, getData: getLeaderboards } = useGetLeaderboardsOnDemand();

  const { isLoading: isGetLeaderboardLoading, data: leaderboard, getData: getLeaderboard } = useGetLeaderboardOnDemand();

  const {
    isLoading: isGetLeaderboardCandidatesLoading,
    data: leaderboardCandidates,
    getData: getLeaderboardCandidates
  } = useGetLeaderboardCandidatesOnDemand();

  const getLeaderboardData = useCallback(
    (leaderboardId: string) => Promise.all([getLeaderboard(leaderboardId), getLeaderboardCandidates(leaderboardId)]),
    [getLeaderboard, getLeaderboardCandidates]
  );

  const { shouldInvoke: shouldInvokeGetMlLeaderboardTemplate } = useApiState(GET_ML_LEADERBOARD_TEMPLATE, {
    organizationId,
    taskId
  });

  useEffect(() => {
    if (shouldInvokeGetMlLeaderboardTemplate) {
      dispatch((_, getState) => {
        getLeaderboardTemplate(taskId).then((apiLeaderboardTemplate) => {
          const { id: apiLeaderboardTemplateId } = apiLeaderboardTemplate;

          if (apiLeaderboardTemplateId) {
            return getLeaderboards(apiLeaderboardTemplateId).then((apiLeaderboards) => {
              if (!isEmptyArray(apiLeaderboards)) {
                const storedLeaderboardId = getStoreLeaderboardId(getState(), taskId);

                const leaderboardId = apiLeaderboards.find(({ id }) => id === storedLeaderboardId)?.id ?? apiLeaderboards[0].id;

                setStoreLeaderboardId(dispatch)(taskId, leaderboardId);

                return getLeaderboardData(leaderboardId);
              }
              return Promise.resolve();
            });
          }
          return Promise.resolve();
        });
      });
    }
  }, [dispatch, getLeaderboardTemplate, getLeaderboardData, getLeaderboards, shouldInvokeGetMlLeaderboardTemplate, taskId]);

  const { selectedLeaderboardId, onSelectionChange } = useTaskSelectedLeaderboardId(taskId as string);

  return (
    <MlTaskLeaderboards
      task={task}
      leaderboardTemplate={leaderboardTemplate}
      leaderboards={leaderboards}
      leaderboard={leaderboard}
      leaderboardCandidates={leaderboardCandidates}
      selectedLeaderboardId={selectedLeaderboardId}
      onSelectedLeaderboardIdChange={(leaderboardId: string) => {
        onSelectionChange(leaderboardId);
        getLeaderboardData(leaderboardId);
      }}
      onCreateLeaderboard={(newLeaderboard) => {
        getLeaderboards(leaderboardTemplate.id).then(() => {
          onSelectionChange(newLeaderboard.id);
          getLeaderboardData(newLeaderboard.id);
        });
      }}
      onUpdateLeaderboard={(updatedLeaderboard) => {
        getLeaderboards(leaderboardTemplate.id).then(() => {
          onSelectionChange(updatedLeaderboard.id);
          getLeaderboardData(updatedLeaderboard.id);
        });
      }}
      isLoadingProps={{
        isGetLeaderboardTemplateLoading,
        isGetLeaderboardsLoading,
        isGetLeaderboardLoading,
        isGetLeaderboardCandidatesLoading
      }}
    />
  );
};

export default MlTaskLeaderboardsContainer;

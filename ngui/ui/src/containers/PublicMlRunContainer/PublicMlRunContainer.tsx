import { useMemo } from "react";
import { useTheme } from "@mui/material/styles";
import { useParams } from "react-router-dom";
import MlTaskRun from "components/MlTaskRun";
import MlTasksService from "services/MlTasksService";
import { getSearchParams } from "utils/network";

const PublicMlRunContainer = () => {
  const theme = useTheme();

  const { useGetTaskRun } = MlTasksService();

  const { runId } = useParams();

  const { organizationId, token: arceeToken } = getSearchParams() as {
    organizationId: string;
    token: string;
  };

  const params = useMemo(
    () => ({
      arceeToken,
    }),
    [arceeToken]
  );

  const { isLoading, isDataReady, run } = useGetTaskRun(organizationId, runId, params);

  return (
    <div
      style={{
        height: "100vh",
        backgroundColor: theme.palette.background.paper,
      }}
    >
      <MlTaskRun
        run={run}
        organizationId={organizationId}
        arceeToken={arceeToken}
        isLoading={isLoading}
        isDataReady={isDataReady}
        isPublicRun
      />
    </div>
  );
};

export default PublicMlRunContainer;

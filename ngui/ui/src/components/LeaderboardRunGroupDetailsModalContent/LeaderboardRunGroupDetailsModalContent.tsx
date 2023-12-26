import { Stack } from "@mui/material";
import { SPACING_2 } from "utils/layouts";
import { Summary, Tabs } from "./components";

const LeaderboardRunGroupDetailsModalContent = ({ taskId, groupDetails, leaderboardDataset }) => {
  const {
    tags = {},
    hyperparams: hyperparameters = {},
    metrics: groupSecondaryMetrics = {},
    primary_metric: groupPrimaryMetric = {},
    coverage
  } = groupDetails;

  return (
    <Stack spacing={SPACING_2}>
      <div>
        <Summary
          tags={tags}
          hyperparameters={hyperparameters}
          metrics={Object.fromEntries([
            ...Object.values(groupPrimaryMetric).map(({ name, value }) => [name, value]),
            ...Object.values(groupSecondaryMetrics).map(({ name, value }) => [name, value])
          ])}
          coverage={coverage}
        />
      </div>
      <div>
        <Tabs taskId={taskId} groupDetails={groupDetails} leaderboardDataset={leaderboardDataset} />
      </div>
    </Stack>
  );
};

export default LeaderboardRunGroupDetailsModalContent;

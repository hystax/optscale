import { Box, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import LeaderboardDatasetDetailsContainer from "containers/LeaderboardDatasetDetailsContainer";
import { useIsAllowed } from "hooks/useAllowedActions";
import { isEmpty as isEmptyArray } from "utils/arrays";
import AddLeaderboardCriteriaButton from "./AddLeaderboardCriteriaButton";
import LeaderboardDatasetCard from "./LeaderboardDatasetCard";

const NoLeaderboards = ({ leaderboardId }) => {
  const isAddLeaderboardCriteriaAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  return (
    <Box>
      <Typography gutterBottom>
        <FormattedMessage id="noLeaderboards" />
      </Typography>
      {isAddLeaderboardCriteriaAllowed && <AddLeaderboardCriteriaButton leaderboardId={leaderboardId} />}
    </Box>
  );
};

const LeaderboardDatasetsListSection = ({
  leaderboard,
  leaderboardDatasets,
  selectedLeaderboardDataset,
  onSelectedLeaderboardDatasetIdChange
}) => {
  const isAddLeaderboardCriteriaAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  return (
    <Box
      sx={{
        display: "flex",
        gap: 1,
        alignItems: "center",
        flexDirection: {
          xs: "row",
          md: "column"
        },
        justifyContent: {
          xs: "space-between",
          md: "normal"
        }
      }}
    >
      {isAddLeaderboardCriteriaAllowed && (
        <AddLeaderboardCriteriaButton
          leaderboardId={leaderboard.id}
          sx={{
            width: {
              md: "100%"
            },
            order: {
              xs: 1,
              md: 0
            }
          }}
        />
      )}
      <Box
        sx={{
          display: "flex",
          gap: 1,
          overflow: "auto",
          minWidth: "150px",
          flexDirection: {
            xs: "row",
            md: "column"
          }
        }}
      >
        {leaderboardDatasets.map((leaderboardDataset) => {
          const isSelected = selectedLeaderboardDataset && leaderboardDataset.id === selectedLeaderboardDataset.id;
          return (
            <LeaderboardDatasetCard
              key={leaderboard.id}
              leaderboardDataset={leaderboardDataset}
              onClick={() => onSelectedLeaderboardDatasetIdChange(leaderboardDataset.id)}
              selected={isSelected}
            />
          );
        })}
      </Box>
    </Box>
  );
};

const LeaderboardDatasets = ({
  leaderboard,
  leaderboardDatasets = [],
  onSelectedLeaderboardDatasetIdChange,
  selectedLeaderboardDataset
}) => (
  <Box
    display="flex"
    sx={{
      flexDirection: {
        xs: "column",
        md: "row"
      },
      gap: {
        md: 2
      }
    }}
  >
    {isEmptyArray(leaderboardDatasets) ? (
      <NoLeaderboards leaderboardId={leaderboard.id} />
    ) : (
      <>
        <LeaderboardDatasetsListSection
          leaderboard={leaderboard}
          leaderboardDatasets={leaderboardDatasets}
          selectedLeaderboardDataset={selectedLeaderboardDataset}
          onSelectedLeaderboardDatasetIdChange={onSelectedLeaderboardDatasetIdChange}
        />
        {selectedLeaderboardDataset && (
          <LeaderboardDatasetDetailsContainer leaderboard={leaderboard} leaderboardDatasetId={selectedLeaderboardDataset.id} />
        )}
      </>
    )}
  </Box>
);

export default LeaderboardDatasets;

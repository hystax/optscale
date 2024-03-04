import { Box, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import LeaderboardDatasetDetails from "components/LeaderboardDatasetDetails";
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
  leaderboardDataset,
  selectedLeaderboardDatasetId,
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
        {leaderboardDatasets.map((datum) => {
          const isSelected = leaderboardDataset && datum.id === selectedLeaderboardDatasetId;
          return (
            <LeaderboardDatasetCard
              key={datum.id}
              leaderboardDataset={datum}
              onClick={() => onSelectedLeaderboardDatasetIdChange(datum.id)}
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
  leaderboardDataset,
  selectedLeaderboardDatasetId,
  leaderboardDatasetDetails,
  onSelectedLeaderboardDatasetIdChange,
  isLoadingProps = {}
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
          leaderboardDataset={leaderboardDataset}
          selectedLeaderboardDatasetId={selectedLeaderboardDatasetId}
          onSelectedLeaderboardDatasetIdChange={onSelectedLeaderboardDatasetIdChange}
        />
        <LeaderboardDatasetDetails
          leaderboard={leaderboard}
          leaderboardDataset={leaderboardDataset}
          leaderboardDatasetDetails={leaderboardDatasetDetails}
          isLoadingProps={{
            isGetLeaderboardDatasetLoading: isLoadingProps.isGetLeaderboardDatasetLoading,
            isGetLeaderboardDatasetDetailsLoading: isLoadingProps.isGetLeaderboardDatasetDetailsLoading
          }}
        />
      </>
    )}
  </Box>
);

export default LeaderboardDatasets;

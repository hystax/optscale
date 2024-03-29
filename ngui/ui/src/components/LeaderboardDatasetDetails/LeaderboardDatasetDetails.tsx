import { Box, Typography } from "@mui/material";
import { Stack } from "@mui/system";
import { FormattedMessage } from "react-intl";
import CopyLeaderboardDatasetIconButton from "components/MlTaskLeaderboard/components/CopyLeaderboardDatasetIconButton";
import DeleteLeaderboardDatasetButton from "components/MlTaskLeaderboard/components/DeleteLeaderboardDatasetButton";
import EditLeaderboardDatasetIconButton from "components/MlTaskLeaderboard/components/EditLeaderboardDatasetIconButton";
import LeaderboardDatasetDetailsTable from "components/MlTaskLeaderboard/components/LeaderboardDatasetDetailsTable";
import SubTitle from "components/SubTitle";
import TableLoader from "components/TableLoader";
import TypographyLoader from "components/TypographyLoader";
import { useIsAllowed } from "hooks/useAllowedActions";

const Title = ({ leaderboard, leaderboardDataset }) => {
  const isManageLeaderboardDatasetAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  return (
    <Box display="flex" alignItems="center" flexWrap="wrap">
      <SubTitle sx={{ whiteSpace: "normal", overflowWrap: "anywhere" }}>{leaderboardDataset.name}</SubTitle>
      {isManageLeaderboardDatasetAllowed && (
        <Box>
          <EditLeaderboardDatasetIconButton leaderboardDataset={leaderboardDataset} />
          <CopyLeaderboardDatasetIconButton leaderboard={leaderboard} leaderboardDataset={leaderboardDataset} />
          <DeleteLeaderboardDatasetButton leaderboardDataset={leaderboardDataset} />
        </Box>
      )}
    </Box>
  );
};

const Datasets = ({ datasets = [], isLoading }) =>
  isLoading ? (
    <TypographyLoader />
  ) : (
    <Typography gutterBottom sx={{ whiteSpace: "normal", overflowWrap: "anywhere" }}>
      <Typography noWrap component="span">
        <FormattedMessage id="datasets" />
        &#58;
      </Typography>
      &nbsp;
      <strong>{datasets.map(({ name }) => name)?.join(", ")}</strong>
    </Typography>
  );

const DetailsTable = ({ isLoading, leaderboardDataset, leaderboardDatasetDetails, leaderboard }) =>
  isLoading ? (
    <TableLoader />
  ) : (
    <LeaderboardDatasetDetailsTable
      leaderboardDataset={leaderboardDataset}
      leaderboardDatasetDetails={leaderboardDatasetDetails}
      primaryMetric={leaderboard.primary_metric}
    />
  );

const LeaderboardDatasetDetails = ({ leaderboard, leaderboardDataset, leaderboardDatasetDetails, isLoadingProps = {} }) => {
  const { isGetLeaderboardDatasetLoading, isGetLeaderboardDatasetDetailsLoading } = isLoadingProps;

  return (
    <Stack overflow="auto" flexGrow={1} spacing={1}>
      <div>
        {isGetLeaderboardDatasetLoading ? (
          <TypographyLoader />
        ) : (
          <Title leaderboard={leaderboard} leaderboardDataset={leaderboardDataset} isLoading={isGetLeaderboardDatasetLoading} />
        )}
      </div>
      <div>
        <Datasets datasets={leaderboardDataset.datasets} isLoading={isGetLeaderboardDatasetLoading} />
      </div>
      <div>
        <DetailsTable
          leaderboard={leaderboard}
          leaderboardDataset={leaderboardDataset}
          leaderboardDatasetDetails={leaderboardDatasetDetails}
          isLoading={isGetLeaderboardDatasetLoading || isGetLeaderboardDatasetDetailsLoading}
        />
      </div>
    </Stack>
  );
};

export default LeaderboardDatasetDetails;

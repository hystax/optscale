import { Paper, Typography } from "@mui/material";
import { lighten, useTheme } from "@mui/material/styles";
import DynamicFractionDigitsValue from "components/DynamicFractionDigitsValue";
import SlicedText from "components/SlicedText";

const METRIC_NAME_LENGTH_LIMIT = 25;

const LeaderboardDatasetCard = ({ leaderboardDataset, onClick, selected, isLoading }) => {
  const theme = useTheme();

  const { name, primary_metric: { name: primaryMetricName, value: primaryMetricValue } = {} } = leaderboardDataset;

  return (
    <Paper
      elevation={0}
      key={name}
      onClick={onClick}
      sx={{
        border: "1px solid",
        borderColor: selected ? theme.palette.action.selected : "#C4C4C4",
        backgroundColor: selected ? lighten(theme.palette.action.selected, 0.9) : undefined,
        p: 1,
        "&:hover": {
          cursor: "pointer",
          backgroundColor: lighten(theme.palette.action.selected, 0.8)
        }
      }}
    >
      <Typography noWrap>{isLoading ? "loading" : <SlicedText text={name} limit={20} />}</Typography>
      <Typography variant="caption" noWrap>
        <SlicedText text={primaryMetricName} limit={METRIC_NAME_LENGTH_LIMIT} />
        &#58;&nbsp;
        <strong>{primaryMetricValue === null ? "-" : <DynamicFractionDigitsValue value={primaryMetricValue} />}</strong>
      </Typography>
    </Paper>
  );
};

export default LeaderboardDatasetCard;

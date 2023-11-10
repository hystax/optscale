import { Paper } from "@mui/material";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import { useTheme } from "@mui/material/styles";
import { FormattedMessage, FormattedNumber } from "react-intl";
import TitleValue from "components/TitleValue";
import WidgetTitle from "components/WidgetTitle";
import { SUCCESS, WARNING, ERROR } from "utils/constants";
import useStyles from "./AdoptionScore.styles";

const getColor = (fraction) => {
  if (fraction <= 0.5) {
    return ERROR;
  }
  if (fraction <= 0.8) {
    return WARNING;
  }
  return SUCCESS;
};

const AdoptionScore = ({ isLoading, fraction }) => {
  const { classes } = useStyles();

  const theme = useTheme();
  const color = isLoading ? "primary" : getColor(fraction);
  const colorValue = theme.palette[color].main;

  return (
    <Paper className={classes.container}>
      <WidgetTitle>
        <FormattedMessage id="checklist.adoptionScore" />
      </WidgetTitle>
      <Box className={classes.badge} data-test-id="count_finops_score">
        {/* background score circle */}
        <CircularProgress
          size={70}
          variant="determinate"
          value={100}
          style={{ color: colorValue }}
          classes={{ root: classes.circleBack }}
        />
        {/* percentage score circle */}
        <CircularProgress size={70} variant="determinate" value={fraction * 100} style={{ color: colorValue }} />
        <Box className={classes.scoreContainer}>
          {/* preloader */}
          {isLoading && <CircularProgress style={{ color: colorValue }} />}
          {/* value */}
          {!isLoading && (
            <TitleValue
              style={{
                color: fraction === 0 ? colorValue : "inherit" // red text for 0%
              }}
            >
              <FormattedNumber value={fraction} format="percentage" />
            </TitleValue>
          )}
        </Box>
      </Box>
    </Paper>
  );
};

export default AdoptionScore;

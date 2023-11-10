import { Box, Paper, Typography } from "@mui/material";
import Skeleton from "@mui/material/Skeleton";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import QuestionMark from "components/QuestionMark";
import SubTitle from "components/SubTitle";
import { intPercentXofY } from "utils/math";
import useStyles from "./PossibleSavingsCard.styles";

const PossibleSavingsCard = ({ possibleMonthlySavings = 0, thisMonthExpensesForecast = 0, isLoading }) => {
  const percent = Math.min(intPercentXofY(possibleMonthlySavings, thisMonthExpensesForecast), 100);

  const getProgressBarColor = () => {
    if (percent < 15) {
      return "success";
    }
    if (percent < 40) {
      return "warning";
    }
    return "error";
  };

  const { classes } = useStyles({
    progressBar: {
      color: getProgressBarColor(),
      width: `${percent}%`
    }
  });

  const body = (
    <Box>
      <Typography component="div" className={classes.possibleSavingsTitle} gutterBottom>
        <SubTitle align="center">
          <FormattedMessage id="possibleMonthlySavings" />
        </SubTitle>
        <QuestionMark messageId="savingsRelativeToThisMonthForecast" />
      </Typography>
      <Paper className={classes.progressBarPaper} variant="outlined">
        <Box className={classes.progressBar} />
        <Box p={1} position="relative" display="flex" justifyContent="space-between">
          <Typography variant="subtitle1" fontWeight="bold">
            <FormattedMoney value={possibleMonthlySavings} />
          </Typography>
          <Typography variant="subtitle1" fontWeight="bold">
            <FormattedMoney value={thisMonthExpensesForecast} />
          </Typography>
        </Box>
      </Paper>
    </Box>
  );

  return isLoading ? (
    <Skeleton width="100%" variant="rectangular">
      {body}
    </Skeleton>
  ) : (
    body
  );
};

export default PossibleSavingsCard;

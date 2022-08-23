import React, { useEffect, useState } from "react";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import { useIntl } from "react-intl";
import { useDispatch, useSelector } from "react-redux";
import QuestionMark from "components/QuestionMark";
import Selector from "components/Selector";
import WrapperCard from "components/WrapperCard";
import { EXPENSES_BREAKDOWN_PERIODS } from "utils/constants";
import { getQueryParams, updateQueryParams } from "utils/network";
import { changePeriodType } from "./actionCreator";
import useStyles from "./ExpensesBreakdownByPeriodWidget.styles";
import { EXPENSES_BREAKDOWN_PERIOD_TYPE } from "./reducer";

const PERIOD_TYPE_QUERY_PARAMETER_NAME = "expenses";

const ExpensesBreakdownByPeriodWidget = ({ render, titlePdfId }) => {
  const dispatch = useDispatch();
  const intl = useIntl();
  const { [PERIOD_TYPE_QUERY_PARAMETER_NAME]: periodTypeQueryParameter } = getQueryParams();

  const { classes } = useStyles();

  const periodTypeState = useSelector((state) => state[EXPENSES_BREAKDOWN_PERIOD_TYPE]);

  const [periodType, setPeriodType] = useState(
    [Object.values(EXPENSES_BREAKDOWN_PERIODS)].includes(periodTypeQueryParameter) ? periodTypeQueryParameter : periodTypeState
  );

  useEffect(() => {
    updateQueryParams({
      [PERIOD_TYPE_QUERY_PARAMETER_NAME]: periodType
    });
    dispatch(changePeriodType(periodType));
  }, [dispatch, periodType]);

  return (
    <WrapperCard
      title={
        <Box display="flex" alignItems="center">
          <Selector
            data={{
              selected: periodType,
              items: Object.values(EXPENSES_BREAKDOWN_PERIODS).map((periodName) => ({
                name: intl.formatMessage({ id: periodName }),
                value: periodName
              }))
            }}
            variant="standard"
            dataTestId="select_org"
            onChange={(value) => {
              setPeriodType(value);
            }}
            customClass={classes.selector}
          />
          {intl.formatMessage({ id: "expenses" }).toLowerCase()}
          <QuestionMark
            messageId="expensesBreakdownBarChartDescription"
            messageValues={{ periodType: intl.formatMessage({ id: periodType }) }}
          />
        </Box>
      }
      titlePdf={{
        id: titlePdfId,
        renderData: () => ({
          titleText: {
            [EXPENSES_BREAKDOWN_PERIODS.DAILY]: "dailyExpenses",
            [EXPENSES_BREAKDOWN_PERIODS.WEEKLY]: "weeklyExpenses",
            [EXPENSES_BREAKDOWN_PERIODS.MONTHLY]: "monthlyExpenses"
          }[periodType]
        })
      }}
    >
      {render(periodType)}
    </WrapperCard>
  );
};

ExpensesBreakdownByPeriodWidget.propTypes = {
  render: PropTypes.func.isRequired,
  titlePdfId: PropTypes.string
};

export default ExpensesBreakdownByPeriodWidget;

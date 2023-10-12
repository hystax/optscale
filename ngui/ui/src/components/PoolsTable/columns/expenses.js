import React from "react";
import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import ProgressBar from "components/ProgressBar";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";
import { FORMATTED_MONEY_TYPES, SUCCESS } from "utils/constants";
import { percentXofY, round } from "utils/math";

const expenses = () => ({
  header: <TextWithDataTestId dataTestId="lbl_expenses" messageId="expensesThisMonth" />,
  accessorKey: "cost",
  cell: ({
    row: {
      original: { cost = 0, hasLimit, limit = 0, remain }
    }
  }) => {
    const expensesCommonWidthStyles = { width: "100%", maxWidth: "150px" };
    const expensesTextStyles = { fontWeight: "bold", display: "block", textAlign: "center" };
    const costFormatted = <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cost} />;
    if (limit === 0 && !hasLimit) {
      return (
        <Tooltip title={<FormattedMessage id="thisPoolHasNoLimit" />}>
          <Typography sx={{ ...expensesTextStyles, ...expensesCommonWidthStyles }}>{costFormatted}</Typography>
        </Tooltip>
      );
    }

    if (cost > limit) {
      const timesMoreValue = round(percentXofY(cost, limit), 1);
      const timesMore = timesMoreValue !== 1 ? ` (x${timesMoreValue})` : "";
      return (
        <Tooltip
          title={
            <FormattedMessage
              id="thisMonthExpensesExceedThePoolLimitBy"
              values={{
                value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={-remain} />
              }}
            />
          }
        >
          <Typography sx={{ ...expensesTextStyles, ...expensesCommonWidthStyles }} color="error">
            {costFormatted}
            {timesMore}
          </Typography>
        </Tooltip>
      );
    }

    const xDividedByY = cost / limit;
    const percent = xDividedByY * 100;
    return (
      <ProgressBar
        wrapperSx={expensesCommonWidthStyles}
        tooltip={{
          show: cost !== 0,
          value: (
            <FormattedMessage
              id="leftX"
              values={{
                value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={remain} />
              }}
            />
          )
        }}
        color={SUCCESS}
        value={percent}
      >
        {costFormatted}
      </ProgressBar>
    );
  },
  defaultSort: "desc",
  columnSelector: {
    accessor: "cost",
    messageId: "expensesThisMonth",
    dataTestId: "btn_toggle_cost"
  }
});

export default expenses;

import WarningAmberOutlinedIcon from "@mui/icons-material/WarningAmberOutlined";
import { Box, Stack, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useMoneyFormatter } from "components/FormattedMoney";
import IconLabel from "components/IconLabel";
import QuestionMark from "components/QuestionMark";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { CURRENCY } from "utils/currency";
import { parse, SHORT_MONTHS } from "utils/datetime";
import { SPACING_1 } from "utils/layouts";
import { isEmptyObject } from "utils/objects";

const currentMonthIndex = 0;

const formatMonthLabel = (yearMonth: string) => {
  const [year, month] = yearMonth.split("-");
  const monthIndex = parseInt(month, 10) - 1;
  const monthName = SHORT_MONTHS[monthIndex];
  const label = `${monthName} ${year}`;
  return label;
};

const ExpensesLimitLabel = ({ color, value, limit }: { color?: string; value: number; limit: number }) => {
  const moneyFormatter = useMoneyFormatter();

  return (
    <Typography color={color}>
      <FormattedMessage id="currentMonthExpenses" />
      :&nbsp;
      <FormattedMessage
        id="value / value"
        values={{
          value1: moneyFormatter(FORMATTED_MONEY_TYPES.COMMON, value, { format: CURRENCY.USD }),
          value2: moneyFormatter(FORMATTED_MONEY_TYPES.COMMON, limit, { format: CURRENCY.USD }),
        }}
      />
    </Typography>
  );
};

const ExpensesLimit = ({
  monthExpenses,
  monthlyExpensesLimit,
}: {
  monthExpenses: Record<string, number>;
  monthlyExpensesLimit: number;
}) => {
  const moneyFormatter = useMoneyFormatter();

  if (isEmptyObject(monthExpenses)) {
    return <ExpensesLimitLabel value={0} limit={monthlyExpensesLimit} />;
  }

  const monthsExpensesDataArray = Object.keys(monthExpenses)
    .sort((rawA, rawB) => {
      const dataA = parse(rawA, "yyyy-MM", new Date());
      const dataB = parse(rawB, "yyyy-MM", new Date());

      return dataB.getTime() - dataA.getTime();
    })
    .map((monthKey) => {
      const expenses = monthExpenses[monthKey] ?? 0;

      return {
        expenses,
        label: formatMonthLabel(monthKey),
        isExceeded: expenses > monthlyExpensesLimit,
      };
    });

  const isCurrentMonthExpensesExceeded = monthsExpensesDataArray[currentMonthIndex].isExceeded;
  const someOtherMonthExpensesExceeded = monthsExpensesDataArray.slice(1).some((month) => month.isExceeded);

  const shouldShowHelp = isCurrentMonthExpensesExceeded || someOtherMonthExpensesExceeded;

  const renderLabel = () => {
    const currentMonthExpenses = monthsExpensesDataArray[currentMonthIndex].expenses;

    if (isCurrentMonthExpensesExceeded) {
      return (
        <IconLabel
          icon={<WarningAmberOutlinedIcon fontSize="inherit" color="error" />}
          label={<ExpensesLimitLabel value={currentMonthExpenses} limit={monthlyExpensesLimit} color="error" />}
        />
      );
    }

    if (someOtherMonthExpensesExceeded) {
      return (
        <IconLabel
          icon={<WarningAmberOutlinedIcon fontSize="inherit" color="error" />}
          label={
            <Typography color="error">
              <FormattedMessage id="monthlyExpensesLimitExceeded" />
            </Typography>
          }
        />
      );
    }

    return <ExpensesLimitLabel value={currentMonthExpenses} limit={monthlyExpensesLimit} />;
  };

  return (
    <Box display="flex" alignItems="center">
      {renderLabel()}
      {shouldShowHelp && (
        <QuestionMark
          tooltipText={
            <Stack spacing={SPACING_1}>
              <Typography component="span">
                <FormattedMessage
                  id="monthlyExpensesLimitExceededMessage"
                  values={{
                    limit: <strong>{moneyFormatter(FORMATTED_MONEY_TYPES.COMMON, monthlyExpensesLimit)}</strong>,
                  }}
                />
              </Typography>
              <Box
                component="ul"
                sx={{
                  paddingInlineStart: (theme) => theme.spacing(2),
                  listStyleType: "'-  '",
                  "& > li + li": {
                    marginTop: (theme) => theme.spacing(0.5),
                  },
                }}
              >
                {monthsExpensesDataArray.map((month) => (
                  <Typography component="li" key={month.label} color={month.isExceeded ? "error" : "inherit"}>
                    {`${month.label}: ${moneyFormatter(FORMATTED_MONEY_TYPES.COMMON, month.expenses)}`}
                  </Typography>
                ))}
              </Box>
            </Stack>
          }
          fontSize="small"
          color="secondary"
        />
      )}
    </Box>
  );
};

export default ExpensesLimit;

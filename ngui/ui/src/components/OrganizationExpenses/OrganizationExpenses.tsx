import ExitToAppOutlinedIcon from "@mui/icons-material/ExitToAppOutlined";
import { useTheme } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import CanvasBarChart from "components/CanvasBarChart";
import FormattedMoney, { useMoneyFormatter } from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import WrapperCard from "components/WrapperCard";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { intl } from "translations/react-intl-config";
import { EXPENSES_BY_POOL } from "urls";
import { AXIS_FORMATS } from "utils/charts";
import { EXPENSES_PERIOD, LAST_MONTH, THIS_MONTH, THIS_MONTH_FORECAST, FORMATTED_MONEY_TYPES } from "utils/constants";
import { getUTCShortMonthFromTimestamp } from "utils/datetime";
import { isEmpty as isEmptyObject, idx } from "utils/objects";

// Ensure we display bar chart in order
const getOrderedExpenses = (expenses) => ({
  [LAST_MONTH]: expenses[LAST_MONTH],
  [THIS_MONTH]: expenses[THIS_MONTH],
  [THIS_MONTH_FORECAST]: expenses[THIS_MONTH_FORECAST]
});

const HEIGHT = 35;
const MARGIN = { top: 20, bottom: 30, right: 10, left: 55 } as const;

const getChartData = (expenses) =>
  Object.entries(getOrderedExpenses(expenses)).map(([periodName, expensesData = {}]) => {
    const monthName = getUTCShortMonthFromTimestamp(expensesData.date);
    return {
      ...expensesData,
      expensesPeriod: EXPENSES_PERIOD[periodName],
      index: periodName === THIS_MONTH_FORECAST ? intl.formatMessage({ id: "monthNameForecast" }, { monthName }) : monthName
    };
  });

const OrganizationExpenses = ({ data, isLoading }) => {
  const moneyFormatter = useMoneyFormatter();

  const { currency } = useOrganizationInfo();
  const theme = useTheme();
  const { expenses = {}, total = 0 } = data;

  const navigate = useNavigate();

  const goToExpensesByPool = () => navigate(EXPENSES_BY_POOL);

  const isEmptyChart = isEmptyObject(expenses) || Object.values(expenses).every((expense) => expense.total === 0);
  const chartData = isEmptyChart ? [] : getChartData(expenses);

  const renderTooltipBody = (sectionData) => (
    <KeyValueLabel
      value={<FormattedMoney value={sectionData.value} type={FORMATTED_MONEY_TYPES.COMMON} />}
      keyText={intl.formatMessage({ id: idx(["data", "expensesPeriod"], sectionData) })}
    />
  );

  return (
    <WrapperCard
      needAlign
      title={<FormattedMessage id="organizationExpenses" />}
      titleButton={{
        type: "icon",
        tooltip: {
          title: <FormattedMessage id="goToOrganizationExpenses" />
        },
        buttonProps: {
          icon: <ExitToAppOutlinedIcon />,
          isLoading,
          onClick: goToExpensesByPool,
          dataTestId: "btn_go_to_org_expenses"
        }
      }}
      dataTestIds={{
        wrapper: "block_org_expenses",
        title: "lbl_org_expenses"
      }}
      elevation={0}
    >
      <CanvasBarChart
        dataTestId="block_org_expenses_chart"
        indexBy="index"
        palette={theme.palette.monoChart}
        data={chartData}
        keys={["total"]}
        renderTooltipBody={renderTooltipBody}
        style={{ height: HEIGHT, margin: MARGIN }}
        axisFormat={AXIS_FORMATS.MONEY}
        isLoading={isLoading}
        enableTotals
        valueFormat={(value) => moneyFormatter(FORMATTED_MONEY_TYPES.COMPACT, value)}
        maxValue={total}
        thresholdMarker={{
          value: total,
          format: (value) => intl.formatNumber(value, { format: currency })
        }}
        emptyMessageId="noOrganizationExpensesMessage"
      />
    </WrapperCard>
  );
};

export default OrganizationExpenses;

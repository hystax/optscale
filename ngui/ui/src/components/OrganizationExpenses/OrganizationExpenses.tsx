import ExitToAppOutlinedIcon from "@mui/icons-material/ExitToAppOutlined";
import { useTheme } from "@mui/material";
import Grid from "@mui/material/Grid";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import BarChart from "components/BarChart";
import FormattedMoney from "components/FormattedMoney";
import KeyValueChartTooltipBody from "components/KeyValueChartTooltipBody";
import WrapperCard from "components/WrapperCard";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { intl } from "translations/react-intl-config";
import { EXPENSES_BY_POOL } from "urls";
import { checkEveryValueByKey } from "utils/arrays";
import { AXIS_FORMATS } from "utils/charts";
import { EXPENSES_PERIOD, LAST_MONTH, THIS_MONTH, THIS_MONTH_FORECAST, FORMATTED_MONEY_TYPES } from "utils/constants";
import { getUTCShortMonthFromTimestamp } from "utils/datetime";
import { isEmpty, idx } from "utils/objects";

// Ensure we display bar chart in order
const getOrderedExpenses = (expenses) => ({
  [LAST_MONTH]: expenses[LAST_MONTH],
  [THIS_MONTH]: expenses[THIS_MONTH],
  [THIS_MONTH_FORECAST]: expenses[THIS_MONTH_FORECAST]
});

const SPACING_BETWEEN_LABEL_AND_BAR = 10;
const HEIGHT = 35;

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
  const { currency = "USD" } = useOrganizationInfo();
  const theme = useTheme();
  const { expenses = {}, total = 0 } = data;

  const navigate = useNavigate();

  const goToExpensesByPool = () => navigate(EXPENSES_BY_POOL);

  const chartData = !isEmpty(expenses) ? getChartData(expenses) : [];

  const renderTooltipBody = (sectionData) => {
    const fieldTooltipText = ["data", "expensesPeriod"];
    const { id } = sectionData;
    const text = fieldTooltipText ? intl.formatMessage({ id: idx(fieldTooltipText, sectionData) }) : intl.formatMessage({ id });
    return <KeyValueChartTooltipBody value={sectionData.value} text={text} />;
  };

  const renderContent = !checkEveryValueByKey(chartData, "total", 0) ? (
    <Grid container>
      <Grid data-test-id="grd_org_exp" item xs={12}>
        <BarChart
          palette={theme.palette.monoChart}
          data={chartData}
          keys={["total"]}
          indexBy="index"
          renderTooltipBody={renderTooltipBody}
          markers={{
            alwaysDisplay: true,
            value: total,
            format: currency
          }}
          style={{ height: HEIGHT, margin: { top: 20, bottom: 30, right: 10, left: 55 } }}
          enableLabel
          label={({ value }) => (
            <tspan y={-SPACING_BETWEEN_LABEL_AND_BAR}>
              <FormattedMoney disableTooltip value={value} type={FORMATTED_MONEY_TYPES.COMPACT} />
            </tspan>
          )}
          dataTestId="block_org_expenses_chart"
          axisFormat={AXIS_FORMATS.MONEY}
        />
      </Grid>
    </Grid>
  ) : (
    <Grid container>
      <Grid item xs={12}>
        <Typography>
          <FormattedMessage id="noOrganizationExpensesMessage" />
        </Typography>
      </Grid>
    </Grid>
  );

  const renderLoading = (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Skeleton variant="rectangular" height={theme.spacing(HEIGHT)} />
      </Grid>
    </Grid>
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
      {isLoading ? renderLoading : renderContent}
    </WrapperCard>
  );
};

export default OrganizationExpenses;

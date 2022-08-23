import React, { useMemo } from "react";
import Grid from "@mui/material/Grid";
import Link from "@mui/material/Link";
import { useTheme } from "@mui/material/styles";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import Circle from "components/Circle";
import CloudLabel from "components/CloudLabel";
import FormattedMoney from "components/FormattedMoney";
import KeyValueChartTooltipBody from "components/KeyValueChartTooltipBody";
import PieChart from "components/PieChart";
import PieChartLoader from "components/PieChartLoader";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import WrapperCard from "components/WrapperCard";
import { EXPENSES_BY_CLOUD, CLOUD_ACCOUNTS } from "urls";
import { sortObjects, getLength } from "utils/arrays";
import { getPieChartOptions, getColorScale, addEntityIconToTooltipKey } from "utils/charts";
import { FORMATTED_MONEY_TYPES } from "utils/constants";

const DATA_SOURCE_LIMIT = 5;
const CHART_HEIGHT = 28;

const renderTooltipBody = (sectionData) => {
  const {
    value,
    label,
    data: { details }
  } = sectionData;
  return <KeyValueChartTooltipBody value={value} text={addEntityIconToTooltipKey(label, details, "cloud")} />;
};

const renderContent = ({ palette, cleanChartData, cloudAccounts, cloudAccountLegendColumns, thereAreMoreCloudAccounts }) => (
  <Grid container spacing={2}>
    <Grid data-test-id="grd_exp" item xs={12} sm={4} lg={12} xl={4}>
      <PieChart
        palette={palette}
        data={cleanChartData}
        style={{ height: CHART_HEIGHT }}
        renderTooltipBody={renderTooltipBody}
      />
    </Grid>
    <Grid item xs={12} sm={8} lg={12} xl={8}>
      <Table
        columns={cloudAccountLegendColumns}
        data={cloudAccounts}
        localization={{
          emptyMessageId: "noExpensesAvailable"
        }}
        dataTestIds={{
          container: "table_clouds"
        }}
        showAllLink={thereAreMoreCloudAccounts ? CLOUD_ACCOUNTS : undefined}
      />
    </Grid>
  </Grid>
);

const renderLoading = (cloudAccountLegendColumns) => (
  <Grid data-test-id="grd_exp" container spacing={2}>
    <Grid item xs={12} xl={4}>
      <PieChartLoader height={CHART_HEIGHT} />
    </Grid>
    <Grid item xs={12} xl={8}>
      <TableLoader columnsCounter={cloudAccountLegendColumns.length} />
    </Grid>
  </Grid>
);

const CloudExpenses = ({ isLoading, cloudAccounts, needCardAlign }) => {
  const theme = useTheme();

  const cloudAccountLegendColumns = useMemo(() => {
    const colorScale = getColorScale(theme.palette.chart);
    return [
      {
        Header: <FormattedMessage id="dataSource" />,
        accessor: "name",
        Cell: ({
          row: {
            original: { id, name, type, details: { cost } = {} },
            index
          }
        }) => (
          <CloudLabel
            id={id}
            name={name}
            type={type}
            dataTestId={`link_cloud_${index}`}
            startAdornment={cost ? <Circle color={colorScale(id)} mr={1} /> : null}
          />
        )
      },
      {
        Header: <FormattedMessage id="monthToDate" />,
        Cell: ({ cell: { value } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={value} />,
        defaultSort: "desc",
        accessor: "details.cost"
      }
    ];
  }, [theme.palette.chart]);

  const sortedCloudAccounts = useMemo(
    () =>
      sortObjects({
        array: cloudAccounts,
        field: ["details", "cost"]
      }).slice(0, DATA_SOURCE_LIMIT),
    [cloudAccounts]
  );

  const { palette, data: cleanChartData } = getPieChartOptions({
    colors: theme.palette.chart,
    sourceData: sortedCloudAccounts,
    valueField: ["details", "cost"],
    labelField: "name"
  });

  const chartDataLength = getLength(cleanChartData);

  return chartDataLength < 1 && !isLoading ? null : (
    <WrapperCard
      needAlign={needCardAlign}
      dataTestIds={{
        wrapper: "div_cloud_exp",
        title: "lbl_cloud_exp",
        button: "btn_cloud_exp"
      }}
      title={
        <Link color="primary" to={EXPENSES_BY_CLOUD} component={RouterLink} data-test-id="link_cloud_expenses">
          <FormattedMessage id="expensesBySource" />
        </Link>
      }
    >
      {isLoading
        ? renderLoading(cloudAccountLegendColumns)
        : renderContent({
            palette,
            cleanChartData,
            cloudAccounts: sortedCloudAccounts,
            cloudAccountLegendColumns,
            thereAreMoreCloudAccounts: cloudAccounts.length > 3
          })}
    </WrapperCard>
  );
};

CloudExpenses.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  needCardAlign: PropTypes.bool.isRequired,
  cloudAccounts: PropTypes.array.isRequired
};

export default CloudExpenses;

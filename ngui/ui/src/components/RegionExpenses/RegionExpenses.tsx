import { useMemo } from "react";
import ListAltOutlinedIcon from "@mui/icons-material/ListAltOutlined";
import Grid from "@mui/material/Grid";
import Skeleton from "@mui/material/Skeleton";
import { useTheme } from "@mui/material/styles";
import { FormattedMessage, FormattedNumber } from "react-intl";
import { useNavigate } from "react-router-dom";
import CloudLabel from "components/CloudLabel";
import ExpensesTableHeader from "components/ExpensesTableHeader";
import FormattedMoney from "components/FormattedMoney";
import IconButton from "components/IconButton";
import MapLegend from "components/MapLegend";
import RegionExpensesMap from "components/RegionExpensesMap";
import SummaryGrid from "components/SummaryGrid";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TypographyLoader from "components/TypographyLoader";
import { useReactiveDefaultDateRange } from "hooks/useReactiveDefaultDateRange";
import { intl } from "translations/react-intl-config";
import { getResourcesExpensesUrl } from "urls";
import { getColorScale } from "utils/charts";
import {
  REGION_FILTER,
  SUMMARY_VALUE_COMPONENT_TYPES,
  FORMATTED_MONEY_TYPES,
  EMPTY_UUID,
  DATE_RANGE_TYPE
} from "utils/constants";
import { SPACING_2, getPoolColorStatus } from "utils/layouts";
import { REGION_EXPENSES_HEIGHT } from "utils/maps";
import { percentXofY, intPercentXofY } from "utils/math";

const getGoToExpensesLink = (name, startDate, endDate) =>
  getResourcesExpensesUrl({
    computedParams: `${REGION_FILTER}=${name}`,
    sStartDate: startDate,
    sEndDate: endDate
  });

const getFilteredMarkers = (markers, total, getColor) =>
  markers
    .filter((marker) => marker.total)
    .map((marker) => ({ ...marker, percent: percentXofY(marker.total, total), color: getColor(marker.type) }));

const getColumns = (navigate, startDate, endDate) => [
  {
    header: intl.formatMessage({ id: "name" }),
    accessorKey: "name",
    cell: ({ row: { original }, cell }) => {
      const value = cell.getValue();

      return original.type ? <CloudLabel label={value} type={original.type} /> : (value ?? <FormattedMessage id="(not set)" />);
    }
  },
  {
    header: <ExpensesTableHeader startDateTimestamp={startDate} endDateTimestamp={endDate} />,
    accessorKey: "total",
    cell: ({ cell }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue()} />,
    defaultSort: "desc"
  },
  {
    header: intl.formatMessage({ id: "percent" }),
    accessorKey: "percent",
    cell: ({ cell }) => <FormattedNumber value={cell.getValue()} format="percentage" />
  },
  {
    header: intl.formatMessage({ id: "actions" }),
    id: "actions",
    cell: ({ row: { original } }) => (
      <IconButton
        onClick={() => navigate(getGoToExpensesLink(original.id === null ? EMPTY_UUID : original.name, startDate, endDate))}
        icon={<ListAltOutlinedIcon />}
        tooltip={{
          show: true,
          value: <FormattedMessage id="showResources" />
        }}
      />
    ),
    enableSorting: true
  }
];

const RegionExpenses = ({ expenses, isLoading = false }) => {
  const navigate = useNavigate();
  const theme = useTheme();

  const { regions: markers = [], total = 0, previous_total: previousTotal = 0 } = expenses;
  const dates = useReactiveDefaultDateRange(DATE_RANGE_TYPE.EXPENSES);
  const [startDateTimestamp, endDateTimestamp] = dates;
  const columns = useMemo(() => getColumns(navigate, dates[0], dates[1]), [navigate, dates]);

  const data = useMemo(() => {
    const getColor = getColorScale(theme.palette.chart);

    return getFilteredMarkers(markers, total, getColor);
  }, [markers, theme.palette.chart, total]);

  const percent = intPercentXofY(total, previousTotal);

  const summaryData = [
    {
      key: "totalExpensesForSelectedPeriod",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: total
      },
      color: getPoolColorStatus(percent),
      captionMessageId: "totalExpensesForSelectedPeriod",
      isLoading
    },
    {
      key: "totalExpensesForPreviousPeriod",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: previousTotal
      },
      captionMessageId: "totalExpensesForPreviousPeriod",
      isLoading
    }
  ];

  const notSetSum = markers.find((marker) => marker.id === EMPTY_UUID)?.total || 0;
  if (notSetSum !== 0 || isLoading) {
    summaryData.push({
      key: "expensesWithoutRegion",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: notSetSum
      },
      captionMessageId: "expensesWithoutRegion",
      isLoading
    });
  }

  return (
    <>
      <Grid direction="row" container spacing={SPACING_2} justifyContent="space-between">
        <Grid item>
          <SummaryGrid summaryData={summaryData} />
        </Grid>
        <Grid item xs={12}>
          {isLoading ? <TypographyLoader linesCount={1} /> : <MapLegend markers={data} />}
        </Grid>
        <Grid item xs={12}>
          {isLoading ? (
            <Skeleton variant="rectangular" height={REGION_EXPENSES_HEIGHT} />
          ) : (
            <RegionExpensesMap
              markers={data}
              defaultCenter={{ lat: 0, lng: 0 }}
              defaultZoom={1}
              startDateTimestamp={startDateTimestamp}
              endDateTimestamp={endDateTimestamp}
            />
          )}
        </Grid>
        <Grid item xs={12}>
          <FormattedMessage
            id="summaryBy"
            values={{
              name: "region"
            }}
          />
          {isLoading ? (
            <TableLoader columnsCounter={columns.length} showHeader />
          ) : (
            <Table
              data={data}
              columns={columns}
              localization={{
                emptyMessageId: "noRegionExpenses"
              }}
              pageSize={50}
            />
          )}
        </Grid>
      </Grid>
    </>
  );
};

export default RegionExpenses;

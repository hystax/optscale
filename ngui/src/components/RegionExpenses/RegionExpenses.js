import React, { useMemo } from "react";
import ListAltOutlinedIcon from "@mui/icons-material/ListAltOutlined";
import Grid from "@mui/material/Grid";
import Skeleton from "@mui/material/Skeleton";
import { useTheme } from "@mui/material/styles";
import PropTypes from "prop-types";
import { FormattedMessage, FormattedNumber } from "react-intl";
import { useNavigate } from "react-router-dom";
import CloudLabel from "components/CloudLabel";
import { getBasicRangesSet } from "components/DateRangePicker/defaults";
import ExpensesTableHeader from "components/ExpensesTableHeader";
import FormattedMoney from "components/FormattedMoney";
import IconButton from "components/IconButton";
import MapLegend from "components/MapLegend";
import PageContentWrapper from "components/PageContentWrapper";
import RegionExpensesMap from "components/RegionExpensesMap";
import SummaryGrid from "components/SummaryGrid";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TypographyLoader from "components/TypographyLoader";
import WrapperCard from "components/WrapperCard";
import RangePickerFormContainer from "containers/RangePickerFormContainer";
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
    Header: intl.formatMessage({ id: "name" }),
    accessor: "name",
    Cell: ({ row: { original }, cell: { value } }) =>
      original.type ? <CloudLabel label={value} type={original.type} /> : value ?? <FormattedMessage id="(not set)" />
  },
  {
    Header: <ExpensesTableHeader startDateTimestamp={startDate} endDateTimestamp={endDate} />,
    accessor: "total",
    Cell: ({ cell: { value } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={value} />,
    defaultSort: "desc"
  },
  {
    Header: intl.formatMessage({ id: "percent" }),
    accessor: "percent",
    Cell: ({ cell: { value } }) => <FormattedNumber value={value} format="percentage" />
  },
  {
    Header: intl.formatMessage({ id: "actions" }),
    id: "actions",
    Cell: ({ row: { original } }) => (
      <IconButton
        onClick={() => navigate(getGoToExpensesLink(original.id === null ? EMPTY_UUID : original.name, startDate, endDate))}
        icon={<ListAltOutlinedIcon />}
        tooltip={{
          show: true,
          value: <FormattedMessage id="showResources" />
        }}
      />
    ),
    disableSortBy: true
  }
];

const RegionExpenses = ({ expenses, applyFilter, startDateTimestamp, endDateTimestamp, isLoading = false }) => {
  const navigate = useNavigate();
  const theme = useTheme();

  const { regions: markers = [], total = 0, previous_total: previousTotal = 0 } = expenses;

  const columns = useMemo(
    () => getColumns(navigate, startDateTimestamp, endDateTimestamp),
    [navigate, startDateTimestamp, endDateTimestamp]
  );

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
      <PageContentWrapper>
        <Grid direction="row" container spacing={SPACING_2} justifyContent="space-between">
          <Grid item>
            <SummaryGrid summaryData={summaryData} />
          </Grid>
          <Grid item>
            <RangePickerFormContainer
              onApply={applyFilter}
              initialStartDateValue={startDateTimestamp}
              initialEndDateValue={endDateTimestamp}
              rangeType={DATE_RANGE_TYPE.EXPENSES}
              definedRanges={getBasicRangesSet()}
            />
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
            <WrapperCard
              title={
                <FormattedMessage
                  id="summaryBy"
                  values={{
                    name: "region"
                  }}
                />
              }
            >
              {isLoading ? (
                <TableLoader columnsCounter={columns.length} showHeader />
              ) : (
                <Table
                  data={data}
                  columns={columns}
                  localization={{
                    emptyMessageId: "noRegionExpenses"
                  }}
                />
              )}
            </WrapperCard>
          </Grid>
        </Grid>
      </PageContentWrapper>
    </>
  );
};

RegionExpenses.propTypes = {
  expenses: PropTypes.object.isRequired,
  applyFilter: PropTypes.func.isRequired,
  startDateTimestamp: PropTypes.number,
  endDateTimestamp: PropTypes.number,
  isLoading: PropTypes.bool
};

export default RegionExpenses;

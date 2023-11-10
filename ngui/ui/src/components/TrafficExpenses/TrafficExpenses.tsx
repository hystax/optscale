import { useCallback, useEffect, useMemo, useState } from "react";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import { Typography } from "@mui/material";
import Grid from "@mui/material/Grid";
import Skeleton from "@mui/material/Skeleton";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import ButtonGroup from "components/ButtonGroup";
import DashedTypography from "components/DashedTypography";
import FormattedDigitalUnit, { SI_UNITS } from "components/FormattedDigitalUnit";
import FormattedMoney from "components/FormattedMoney";
import SummaryGrid from "components/SummaryGrid";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TrafficExpensesMap from "components/TrafficExpensesMap";
import TrafficFromToLabel from "components/TrafficFromToLabel";
import { useReactiveDefaultDateRange } from "hooks/useReactiveDefaultDateRange";
import { useShowLessThanValue } from "hooks/useShowLessThanValue";
import { TABLE_SELECTION_STATE, useTrafficExpenses } from "hooks/useTrafficExpenses";
import { getResourcesExpensesUrl } from "urls";
import {
  SUMMARY_VALUE_COMPONENT_TYPES,
  CLOUD_ACCOUNT_TYPE,
  FORMATTED_MONEY_TYPES,
  NETWORK_TRAFFIC_FROM_FILTER,
  NETWORK_TRAFFIC_TO_FILTER,
  ANY_NETWORK_TRAFFIC_LOCATION,
  DATE_RANGE_TYPE
} from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import { REGION_EXPENSES_HEIGHT } from "utils/maps";
import { getQueryParams, updateQueryParams } from "utils/network";
import ShowLessThanValueSwitch from "./ShowLessThanValueSwitch";

const getCloudSelectorButtons = (totalCosts, onDataSourceChange) =>
  totalCosts.map(([cloudType, cost]) => ({
    id: cloudType,
    messageId: "value(parenthesisValue)",
    messageValues: {
      value: <FormattedMessage id={CLOUD_ACCOUNT_TYPE[cloudType]} />,
      parenthesisValue: <FormattedMoney value={cost} type={FORMATTED_MONEY_TYPES.COMPACT} disableTooltip />
    },
    action: () => onDataSourceChange(cloudType),
    dataTestId: `${cloudType}_option`
  }));

const DATA_SOURCE_PARAM = "dataSource";

const Summary = ({ isLoading, totalCost, totalUsage }) => {
  const summaryData = [
    {
      key: "totalExpenses",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: totalCost
      },
      captionMessageId: "totalExpenses",
      isLoading
    },
    {
      key: "totalUsage",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMessage,
      valueComponentProps: {
        id: "{value}",
        values: {
          value: <FormattedDigitalUnit value={totalUsage} baseUnit={SI_UNITS.GIGABYTE} />
        }
      },
      captionMessageId: "totalUsage",
      isLoading
    }
  ];

  return <SummaryGrid summaryData={summaryData} />;
};

const TrafficExpenses = ({ expenses, isLoading = false }) => {
  const navigate = useNavigate();

  const { showLessThanValue } = useShowLessThanValue();

  const { traffic_expenses: trafficExpenses = [], total_cost: totalCost = 0, total_usage: totalUsage = 0 } = expenses;

  const { [DATA_SOURCE_PARAM]: dataSourceParam } = getQueryParams();

  const [selectedCloudType, setSelectedCloudType] = useState(dataSourceParam);

  const totalCosts = useMemo(
    () => trafficExpenses.reduce((acc, obj) => ({ ...acc, [obj.cloud_type]: (acc[obj.cloud_type] || 0) + obj.cost }), {}),
    [trafficExpenses]
  );
  const sortedTotalCosts = useMemo(() => Object.entries(totalCosts).sort((a, b) => b[1] - a[1]), [totalCosts]);

  useEffect(() => {
    if (!isLoading && !selectedCloudType) {
      const defaultDataSource = sortedTotalCosts?.[0]?.[0];
      setSelectedCloudType(defaultDataSource);
      updateQueryParams({ [DATA_SOURCE_PARAM]: defaultDataSource });
    }
  }, [isLoading, selectedCloudType, sortedTotalCosts]);

  const expensesFilteredBySelectedCloudType = useMemo(() => {
    const trafficFiltered = showLessThanValue ? trafficExpenses : trafficExpenses.filter(({ cost }) => cost >= 1);
    return trafficFiltered.filter((expense) => expense.cloud_type === selectedCloudType);
  }, [selectedCloudType, trafficExpenses, showLessThanValue]);

  const { markers, onMapClick, tableData, columns, tableSelectionState, onFilterClear, defaultZoom, defaultCenter } =
    useTrafficExpenses(expensesFilteredBySelectedCloudType);

  const onDataSourceChange = useCallback(
    (newDataSource) => {
      setSelectedCloudType(newDataSource);
      updateQueryParams({ [DATA_SOURCE_PARAM]: newDataSource });
      onFilterClear();
    },
    [setSelectedCloudType, onFilterClear]
  );

  const cloudSelectorButtons = useMemo(
    () => getCloudSelectorButtons(sortedTotalCosts, onDataSourceChange),
    [sortedTotalCosts, onDataSourceChange]
  );

  // clearing filters on each showLessThanValue change
  useEffect(() => {
    onFilterClear();
  }, [showLessThanValue, onFilterClear]);

  const buttonsGroup = (
    <ButtonGroup
      buttons={cloudSelectorButtons}
      activeButtonIndex={cloudSelectorButtons.indexOf(cloudSelectorButtons.find((button) => button.id === selectedCloudType))}
    />
  );

  const [startDateTimestamp, endDateTimestamp] = useReactiveDefaultDateRange(DATE_RANGE_TYPE.EXPENSES);
  const goToResourcesHandler = () => {
    const parseLocations = (locations) => [locations].flat().map((location) => `${location}:${selectedCloudType}`);

    const { from: fromLocations, to: toLocations } = tableSelectionState.data;
    const [fromFilters, toFilters] =
      tableSelectionState.state === TABLE_SELECTION_STATE.NOTHING_SELECTED
        ? [ANY_NETWORK_TRAFFIC_LOCATION, ANY_NETWORK_TRAFFIC_LOCATION]
        : [fromLocations && parseLocations(fromLocations), toLocations && parseLocations(toLocations)];

    navigate(
      getResourcesExpensesUrl({
        sStartDate: startDateTimestamp,
        sEndDate: endDateTimestamp,
        [NETWORK_TRAFFIC_FROM_FILTER]: fromFilters,
        [NETWORK_TRAFFIC_TO_FILTER]: toFilters
      })
    );
  };

  const title = (
    <div
      style={{
        display: "flex",
        alignItems: "center"
      }}
    >
      <Typography component="span" sx={{ marginRight: 1 }}>
        {tableSelectionState.state === TABLE_SELECTION_STATE.NOTHING_SELECTED ? (
          <FormattedMessage id="allNetworkTrafficExpenses" />
        ) : (
          <TrafficFromToLabel from={tableSelectionState.labels.from} to={tableSelectionState.labels.to} />
        )}
      </Typography>
      {tableSelectionState.state !== TABLE_SELECTION_STATE.NOTHING_SELECTED && (
        <DashedTypography onClick={onFilterClear} component="span" sx={{ marginRight: 1 }} dataTestId="clearFilter">
          <FormattedMessage id="clearFilter" />
        </DashedTypography>
      )}
      <div style={{ display: "flex", alignItems: "center", cursor: "pointer" }} onClick={goToResourcesHandler}>
        <DashedTypography disablePointerOnHover component="span" dataTestId="lbl_see_resources">
          <FormattedMessage id="seeResources" />
        </DashedTypography>
        <OpenInNewIcon fontSize="small" />
      </div>
    </div>
  );

  return (
    <>
      <Grid direction="row" container spacing={SPACING_2} justifyContent="space-between">
        <Grid item>
          <Summary isLoading={isLoading} totalCost={totalCost} totalUsage={totalUsage} />
        </Grid>
        <Grid item xs={12}>
          {isLoading ? <Skeleton>{buttonsGroup}</Skeleton> : buttonsGroup}
          <ShowLessThanValueSwitch />
        </Grid>
        <Grid item xs={12}>
          {isLoading ? (
            <Skeleton variant="rectangular" height={REGION_EXPENSES_HEIGHT} />
          ) : (
            <TrafficExpensesMap
              markers={markers}
              defaultZoom={defaultZoom}
              defaultCenter={defaultCenter}
              onMapClick={onMapClick}
            />
          )}
        </Grid>
        <Grid item xs={12}>
          {title}
          {isLoading ? (
            <TableLoader columnsCounter={columns.length} showHeader />
          ) : (
            <Table
              data={tableData}
              columns={columns}
              localization={{
                emptyMessageId: showLessThanValue ? "noTrafficExpenses" : "noTrafficExpensesHint"
              }}
            />
          )}
        </Grid>
      </Grid>
    </>
  );
};

export default TrafficExpenses;

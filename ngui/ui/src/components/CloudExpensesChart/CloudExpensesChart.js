import React, { Fragment } from "react";
import Box from "@mui/material/Box";
import Skeleton from "@mui/material/Skeleton";
import { useTheme, darken } from "@mui/material/styles";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import CloudExpensesChartMarker from "components/CloudExpensesChartMarker";
import CloudLabel from "components/CloudLabel";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import Tooltip from "components/Tooltip";
import { isEmpty } from "utils/arrays";
import { getColorScale } from "utils/charts";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { getPoolColorStatus } from "utils/layouts";
import { getDefaultTableData } from "utils/tables";

const SEGMENT_BORDER_WIDTH = "2px";
const SEGMENT_BORDER_STYLE = "solid";

const CHART_BORDER_WIDTH = "5px";
const CHART_BORDER_STYLE = "solid";

const CHART_SEGMENT_HEIGHT = "3rem";

const CloudExpensesChart = ({ cloudAccounts, limit, forecast, isLoading = false }) => {
  const theme = useTheme();

  const colorScale = getColorScale(theme.palette.chart);
  const cloudData = getDefaultTableData(cloudAccounts, ["details", "cost"]);

  const chartBase = Math.max(limit, forecast);

  const chartBorderColor = getPoolColorStatus((forecast / limit) * 100);

  const renderExpensesSegment = (cost, { id, name, type }) => (
    <Tooltip
      title={
        <KeyValueLabel
          component="div"
          renderKey={() => (
            <CloudLabel
              type={type}
              label={
                <FormattedMessage
                  id="valueExpenses"
                  values={{
                    value: name
                  }}
                />
              }
            />
          )}
          value={<FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cost} />}
        />
      }
      placement="top"
    >
      <Box
        width={`${(cost / chartBase) * 100}%`}
        height={CHART_SEGMENT_HEIGHT}
        bgcolor={colorScale(id)}
        border={`${SEGMENT_BORDER_WIDTH} ${SEGMENT_BORDER_STYLE} ${darken(colorScale(id), 0.4)}`}
        borderRight="0"
      />
    </Tooltip>
  );

  const renderForecastSegment = (cloudAccountForecast, cost, { id, name, type }) => (
    <Tooltip
      title={
        <KeyValueLabel
          component="div"
          renderKey={() => (
            <CloudLabel
              type={type}
              label={
                <FormattedMessage
                  id="valueForecast"
                  values={{
                    value: name
                  }}
                />
              }
            />
          )}
          value={<FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cloudAccountForecast} />}
        />
      }
      placement="top"
    >
      <Box
        width={`${((cloudAccountForecast - cost) / chartBase) * 100}%`}
        height={CHART_SEGMENT_HEIGHT}
        bgcolor={darken(colorScale(id), 0.1)}
        border={`${SEGMENT_BORDER_WIDTH} ${SEGMENT_BORDER_STYLE} ${darken(colorScale(id), 0.4)}`}
        borderLeft="0"
      />
    </Tooltip>
  );

  const renderChart = !isEmpty(cloudAccounts) ? (
    <Box
      display="flex"
      alignItems="flex-start"
      position="relative"
      border={`${CHART_BORDER_WIDTH} ${CHART_BORDER_STYLE} ${theme.palette[chartBorderColor].main}`}
    >
      {limit > forecast ? (
        <CloudExpensesChartMarker
          position="top"
          value={limit}
          chartBorderWidth={CHART_BORDER_WIDTH}
          chartSegmentHeight={CHART_SEGMENT_HEIGHT}
          valueMessageId={"limit"}
          chartBase={chartBase}
        />
      ) : (
        <CloudExpensesChartMarker
          position="top"
          value={forecast}
          chartBorderWidth={CHART_BORDER_WIDTH}
          chartSegmentHeight={CHART_SEGMENT_HEIGHT}
          valueMessageId="forecast"
          chartBase={chartBase}
        />
      )}
      {cloudData.map((data) => {
        const { details: { cost = 0, forecast: cloudAccountForecast = 0 } = {}, id } = data;
        return cost !== 0 ? (
          <Fragment key={id}>
            {renderExpensesSegment(cost, data)}
            {renderForecastSegment(cloudAccountForecast, cost, data)}
          </Fragment>
        ) : null;
      })}
      {limit > forecast ? (
        <CloudExpensesChartMarker
          value={forecast}
          chartBorderWidth={CHART_BORDER_WIDTH}
          chartSegmentHeight={CHART_SEGMENT_HEIGHT}
          valueMessageId="forecast"
          chartBase={chartBase}
        />
      ) : (
        <CloudExpensesChartMarker
          value={limit}
          chartBorderWidth={CHART_BORDER_WIDTH}
          chartSegmentHeight={CHART_SEGMENT_HEIGHT}
          valueMessageId="limit"
          chartBase={chartBase}
        />
      )}
    </Box>
  ) : null;

  return isLoading ? <Skeleton variant="rectangular" height={CHART_SEGMENT_HEIGHT} /> : renderChart;
};

CloudExpensesChart.propTypes = {
  cloudAccounts: PropTypes.array.isRequired,
  limit: PropTypes.number.isRequired,
  forecast: PropTypes.number.isRequired,
  isLoading: PropTypes.bool
};

export default CloudExpensesChart;

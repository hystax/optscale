import React, { useMemo } from "react";
import { Typography } from "@mui/material";
import Skeleton from "@mui/material/Skeleton";
import { useTheme as useMuiTheme } from "@mui/material/styles";
import { ResponsiveWrapper, useDimensions } from "@nivo/core";
import { Line as NivoLine, LineDefaultProps } from "@nivo/line";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ChartTooltip from "components/ChartTooltip";
import { useChartTheme } from "hooks/useChartTheme";
import { getFirstAndLastElements as getFirstAndLastArrayElements, isEmpty as isEmptyArray } from "utils/arrays";
import {
  getLineTicks,
  getStackedLineChartMaxValue,
  getColorScale,
  TICK_COUNT,
  calculateOverflowSettings,
  getLineChartMaxValue
} from "utils/charts";

const DEFAULT_POINT_SIZE = 2;

const Line = ({
  data,
  axisBottom,
  axisLeft,
  renderTooltipBody,
  stacked = false,
  shouldRenderOnlyFirstAndLastBottomTickValues = false,
  pointSize = DEFAULT_POINT_SIZE,
  colors,
  yFormat,
  wrapperDimensions,
  margin: partialMargin,
  pointColor,
  highlightsLayer
}) => {
  const theme = useMuiTheme();

  const { height: wrapperHeight, width: wrapperWidth } = wrapperDimensions;
  const chartTheme = useChartTheme();

  const { margin, innerWidth, outerHeight } = useDimensions(wrapperWidth, wrapperHeight, partialMargin);

  const getBottomTickValues = () => {
    // TODO: Investigate behavior if lines have different amount of points
    const lines = data.map((d) => d.data);
    const maxLengthLineData = lines.reduce(
      (maxLengthData, currentData) => (currentData.length > maxLengthData.length ? currentData : maxLengthData),
      lines[0] || []
    );

    const valueIndexBy = "x";

    const calculatedValuesWithOverflow = calculateOverflowSettings({
      data: maxLengthLineData,
      // TODO: calculate overflow based on the formatted X value, not raw
      indexBy: valueIndexBy,
      padding: 0,
      font: {
        fontSize: chartTheme.axis.ticks.text.fontSize,
        fontFamily: chartTheme.axis.ticks.text.fontFamily
      },
      chartWidth: innerWidth
    });

    const getOnlyFirstAndLastTickValues = () => {
      const points = maxLengthLineData.length > 1 ? getFirstAndLastArrayElements(maxLengthLineData) : [...maxLengthLineData];
      return points.map(({ x }) => x);
    };

    return shouldRenderOnlyFirstAndLastBottomTickValues ? getOnlyFirstAndLastTickValues() : calculatedValuesWithOverflow;
  };

  // TODO - without chartWidth > 0 tests fail, investigate
  const bottomTickValues = innerWidth > 0 && getBottomTickValues();

  const maxValueFromData = stacked ? getStackedLineChartMaxValue(data) : getLineChartMaxValue(data);

  const { maxValue, tickValues } = getLineTicks({ height: outerHeight, ticksCount: TICK_COUNT, maxValue: maxValueFromData });

  const defaultPalette = useMemo(() => {
    const colorScale = getColorScale(theme.palette.chart);

    const paletteColors = [...Array(data.length)].map((_, index) => colorScale(index));

    return stacked ? paletteColors.reverse() : paletteColors;
  }, [data.length, stacked, theme.palette.chart]);

  return (
    <NivoLine
      data={data}
      height={wrapperDimensions.height}
      width={wrapperDimensions.width}
      margin={margin}
      enableGridX={false}
      enableSlices="x"
      yScale={{ type: "linear", min: 0, max: maxValue, stacked }}
      colors={typeof colors === "function" ? colors : defaultPalette}
      enableArea
      areaOpacity={0.1}
      useMesh
      sliceTooltip={({ slice }) => <ChartTooltip body={renderTooltipBody({ slice, stacked })} />}
      axisLeft={{ ...axisLeft, tickValues, tickSize: 0 }}
      axisBottom={{ ...axisBottom, tickValues: bottomTickValues }}
      pointSize={pointSize}
      pointColor={pointColor}
      pointBorderWidth={1}
      yFormat={yFormat}
      pointBorderColor={{ from: "serieColor" }}
      theme={chartTheme}
      lineWidth={1}
      layers={[highlightsLayer, ...LineDefaultProps.layers].filter(Boolean)}
    />
  );
};

Line.propTypes = {
  data: PropTypes.array.isRequired,
  renderTooltipBody: PropTypes.func.isRequired,
  axisBottom: PropTypes.shape({
    renderTick: PropTypes.func
  }),
  axisLeft: PropTypes.shape({
    format: PropTypes.func
  }),
  stacked: PropTypes.bool,
  margin: PropTypes.object,
  pointSize: PropTypes.number,
  shouldRenderOnlyFirstAndLastBottomTickValues: PropTypes.bool,
  colors: PropTypes.func,
  yFormat: PropTypes.oneOfType([PropTypes.string, PropTypes.func]),
  wrapperDimensions: PropTypes.object,
  pointColor: PropTypes.string,
  highlightsLayer: PropTypes.func
};

const ResponsiveLine = ({ data, isLoading, dataTestId, emptyMessageId = "noDataToDisplay", style = {}, ...rest }) => {
  const theme = useMuiTheme();
  const { height = 50, margin = { top: 20, right: 35, left: 75, bottom: 50 } } = style;

  return (
    <div
      style={{
        height: theme.spacing(height)
      }}
      data-test-id={dataTestId}
    >
      <ResponsiveWrapper>
        {({ width: wrapperWidth, height: wrapperHeight }) => {
          if (isLoading) {
            return <Skeleton variant="rectangular" height={wrapperHeight} />;
          }
          if (isEmptyArray(data)) {
            return (
              <Typography
                component="div"
                style={{
                  height: "100%",
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center"
                }}
              >
                <FormattedMessage id={emptyMessageId} />
              </Typography>
            );
          }
          return (
            <Line
              wrapperDimensions={{
                width: wrapperWidth,
                height: wrapperHeight
              }}
              data={data}
              margin={margin}
              pointColor={theme.palette.common.white}
              {...rest}
            />
          );
        }}
      </ResponsiveWrapper>
    </div>
  );
};

ResponsiveLine.propTypes = {
  isLoading: PropTypes.bool,
  dataTestId: PropTypes.string,
  style: PropTypes.object,
  data: PropTypes.array.isRequired,
  emptyMessageId: PropTypes.string
};

export default ResponsiveLine;

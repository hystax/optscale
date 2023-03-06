import React, { useMemo } from "react";
import { Typography } from "@mui/material";
import Skeleton from "@mui/material/Skeleton";
import { useTheme as useMuiTheme } from "@mui/material/styles";
import { ResponsiveWrapper, useDimensions } from "@nivo/core";
import { Line as NivoLine, LineDefaultProps } from "@nivo/line";
import { computeXYScalesForSeries } from "@nivo/scales";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ChartTooltip from "components/ChartTooltip";
import { useChartTheme } from "hooks/useChartTheme";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { getColorScale, TICK_COUNT, getLineYTicks, getLineChartBottomTickValues } from "utils/charts";

const DEFAULT_POINT_SIZE = 2;

const useDefaultPalette = (data, stacked) => {
  const theme = useMuiTheme();

  return useMemo(() => {
    const colorScale = getColorScale(theme.palette.chart);

    const paletteColors = [...Array(data.length)].map((_, index) => colorScale(index));

    return stacked ? paletteColors.reverse() : paletteColors;
  }, [data.length, stacked, theme.palette.chart]);
};

const Line = ({
  data,
  axisBottom,
  axisLeft,
  axisRight,
  renderTooltipBody,
  stacked = false,
  shouldRenderOnlyFirstAndLastBottomTickValues = false,
  pointSize = DEFAULT_POINT_SIZE,
  colors,
  yFormat,
  wrapperDimensions,
  margin: partialMargin,
  pointColor,
  highlightsLayer,
  verticalThresholdsLayer,
  enableGridY = true,
  animate = true,
  xScale: xScaleSpec = {
    type: "point",
    min: 0,
    max: "auto"
  }
}) => {
  const { height: wrapperHeight, width: wrapperWidth } = wrapperDimensions;
  const chartTheme = useChartTheme();

  const { margin, innerWidth, outerHeight, innerHeight } = useDimensions(wrapperWidth, wrapperHeight, partialMargin);

  const defaultYScaleSpec = { type: "linear", min: 0, max: "auto", stacked };

  const { xScale, x, y } = computeXYScalesForSeries(data, xScaleSpec, defaultYScaleSpec, innerWidth, innerHeight);

  const { maxValue: calculatedMaxYValue, tickValues: yTickValues } = getLineYTicks({
    ticksCount: TICK_COUNT,
    yMax: stacked ? y.maxStacked : y.max,
    height: outerHeight
  });

  // Override max value in order to add one more vertical line (tick) above lines
  const yScaleSpec = { ...defaultYScaleSpec, max: calculatedMaxYValue };

  const defaultPalette = useDefaultPalette(data, stacked);

  const getAxisBottom = () => {
    if (axisBottom === null) {
      return null;
    }

    const getTickValues = () => {
      // TODO - without chartWidth > 0 tests fail, investigate
      if (innerWidth > 0) {
        return shouldRenderOnlyFirstAndLastBottomTickValues
          ? [x.min, x.max]
          : getLineChartBottomTickValues({
              x,
              scale: xScale,
              font: {
                fontSize: chartTheme.axis.ticks.text.fontSize,
                fontFamily: chartTheme.axis.ticks.text.fontFamily
              },
              axisBottom
            });
      }

      return undefined;
    };

    return {
      ...axisBottom,
      tickValues: getTickValues()
    };
  };

  return (
    <NivoLine
      data={data}
      animate={animate}
      height={wrapperDimensions.height}
      width={wrapperDimensions.width}
      margin={margin}
      enableGridX={false}
      enableGridY={enableGridY}
      enableSlices="x"
      yScale={yScaleSpec}
      /**
       * Use linear scale in order to fill gaps in the chart - https://github.com/plouc/nivo/issues/1026
       *
       * For storybook docs:
       *  By default, xScale is a point scale, but you can switch to linear using the xScale.type property.
       *  It supports irregular intervals while point scale doesn’t.
       *  If you want missing datums to appear as holes instead of connecting defined ones,
       *  you should set their y value to null.
       */
      xScale={xScaleSpec}
      colors={typeof colors === "function" ? colors : defaultPalette}
      enableArea
      areaOpacity={0.1}
      useMesh
      sliceTooltip={({ slice }) => <ChartTooltip body={renderTooltipBody({ slice, stacked })} />}
      axisLeft={axisLeft ? { ...axisLeft, tickValues: yTickValues, tickSize: 0 } : null}
      axisBottom={getAxisBottom()}
      axisRight={
        axisRight
          ? {
              ...axisRight,
              tickValues: yTickValues,
              tickSize: 0
            }
          : null
      }
      pointSize={pointSize}
      pointColor={pointColor}
      pointBorderWidth={1}
      yFormat={yFormat}
      pointBorderColor={{ from: "serieColor" }}
      theme={chartTheme}
      lineWidth={1}
      layers={[highlightsLayer, ...LineDefaultProps.layers, verticalThresholdsLayer].filter(Boolean)}
    />
  );
};

Line.propTypes = {
  data: PropTypes.array.isRequired,
  renderTooltipBody: PropTypes.func.isRequired,
  axisBottom: PropTypes.shape({
    renderTick: PropTypes.func,
    format: PropTypes.func,
    formatString: PropTypes.func
  }),
  axisLeft: PropTypes.shape({
    format: PropTypes.func
  }),
  axisRight: PropTypes.object,
  stacked: PropTypes.bool,
  margin: PropTypes.object,
  pointSize: PropTypes.number,
  shouldRenderOnlyFirstAndLastBottomTickValues: PropTypes.bool,
  colors: PropTypes.func,
  yFormat: PropTypes.oneOfType([PropTypes.string, PropTypes.func]),
  wrapperDimensions: PropTypes.object,
  pointColor: PropTypes.string,
  highlightsLayer: PropTypes.func,
  verticalThresholdsLayer: PropTypes.func,
  xScale: PropTypes.object,
  enableGridY: PropTypes.bool,
  animate: PropTypes.bool
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

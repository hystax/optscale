import { useMemo } from "react";
import { Typography } from "@mui/material";
import Skeleton from "@mui/material/Skeleton";
import { useTheme as useMuiTheme } from "@mui/material/styles";
import { ResponsiveWrapper, useDimensions } from "@nivo/core";
import { ResponsiveLineCanvas } from "@nivo/line";
import { computeXYScalesForSeries } from "@nivo/scales";
import { FormattedMessage } from "react-intl";
import ChartTooltip from "components/ChartTooltip";
import { useChartTheme } from "hooks/useChartTheme";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { getColorScale, TICK_COUNT, getLineYTicks, getLineChartBottomTickValues } from "utils/charts";
import CanvasLayer from "./CanvasLayer";
import SliceTooltipLayer from "./SliceTooltipLayer";

const useDefaultPalette = (data, stacked) => {
  const theme = useMuiTheme();

  return useMemo(() => {
    const colorScale = getColorScale(theme.palette.chart);

    const paletteColors = [...Array(data.length)].map((_, index) => colorScale(index));

    return stacked ? paletteColors.reverse() : paletteColors;
  }, [data.length, stacked, theme.palette.chart]);
};

const DEFAULT_POINT_SIZE = 2;
const DEFAULT_AREA_OPACITY = 0.1;

const useLineDimensions = ({ height, width, margin: partialMargin }) => {
  const { margin, innerWidth, outerHeight, innerHeight, outerWidth } = useDimensions(width, height, partialMargin);

  return {
    margin,
    innerWidth,
    outerHeight,
    innerHeight,
    outerWidth
  };
};

const useXScaleSpec = ({ xScaleSpecProp = {} }) =>
  useMemo(
    () => ({
      type: xScaleSpecProp.type ?? "point",
      min: xScaleSpecProp.min ?? 0,
      max: xScaleSpecProp.max ?? "auto"
    }),
    [xScaleSpecProp.max, xScaleSpecProp.min, xScaleSpecProp.type]
  );

const useYScaleSpec = ({ data, yScaleSpecProp = {} }) =>
  useMemo(() => {
    const yScaleSpec = {
      type: yScaleSpecProp.type ?? "linear",
      min: yScaleSpecProp.min,
      max: yScaleSpecProp.max,
      stacked: yScaleSpecProp.stacked ?? false
    };

    const getAllY = () => {
      const linesData = data.flatMap(({ data: lineData }) => lineData);
      return linesData.map(({ y }) => y);
    };

    const allY = getAllY();

    const allYNegative = allY.every((y) => y < 0);
    const allYPositive = allY.every((y) => y > 0);

    const getMin = () => {
      if (yScaleSpec.min) {
        return yScaleSpec.min;
      }

      if (allYNegative) {
        return "auto";
      }

      if (allYPositive) {
        return 0;
      }

      return "auto";
    };

    const getMax = () => {
      if (yScaleSpec.max) {
        return yScaleSpec.max;
      }
      if (allYNegative) {
        return 0;
      }

      if (allYPositive) {
        return "auto";
      }

      return "auto";
    };

    return {
      ...yScaleSpec,
      min: getMin(),
      max: getMax()
    };
  }, [data, yScaleSpecProp.max, yScaleSpecProp.min, yScaleSpecProp.stacked, yScaleSpecProp.type]);

const useLineYTicks = ({ yScaleSpec: defaultYScaleSpec, outerHeight, y }) => {
  const getYMax = () => {
    if (defaultYScaleSpec.max === "auto") {
      return defaultYScaleSpec.stacked ? y.maxStacked ?? 0 : y.max;
    }
    return defaultYScaleSpec.max;
  };

  const getYMin = () => {
    if (defaultYScaleSpec.min === "auto") {
      return defaultYScaleSpec.stacked ? y.minStacked ?? 0 : y.min;
    }
    return defaultYScaleSpec.min;
  };

  const {
    maxValue: calculatedMaxYValue,
    minValue: calculatedMinYValue,
    tickValues: yTickValues
  } = getLineYTicks({
    ticksCount: TICK_COUNT,
    yMax: getYMax(),
    yMin: getYMin(),
    height: outerHeight
  });

  return {
    yScaleSpec: {
      ...defaultYScaleSpec,
      // Override max value in order to add one more vertical line (tick) above/below lines
      max: calculatedMaxYValue,
      min: calculatedMinYValue
    },
    yTickValues
  };
};

const Line = ({
  data,
  axisBottom: axisBottomSpec = {},
  axisLeft,
  axisRight,
  renderTooltipBody,
  shouldRenderOnlyFirstAndLastBottomTickValues = false,
  pointSize = DEFAULT_POINT_SIZE,
  colors,
  yFormat,
  xFormat,
  wrapperDimensions,
  margin: partialMargin,
  pointColor,
  enableGridY = true,
  overlayLayers = [],
  xScale: xScaleSpecProp,
  yScale: yScaleSpecProp
}) => {
  const chartTheme = useChartTheme();

  const xScaleSpec = useXScaleSpec({ xScaleSpecProp });

  const yScaleSpec = useYScaleSpec({
    data,
    yScaleSpecProp
  });

  const { margin, innerWidth, outerHeight, innerHeight, outerWidth } = useLineDimensions({
    width: wrapperDimensions.width,
    height: wrapperDimensions.height,
    margin: partialMargin
  });

  const { xScale, x, y, series } = useMemo(
    () => computeXYScalesForSeries(data, xScaleSpec, yScaleSpec, innerWidth, innerHeight),
    [data, yScaleSpec, innerHeight, innerWidth, xScaleSpec]
  );

  const { yScaleSpec: updatedYScaleSpec, yTickValues } = useLineYTicks({
    yScaleSpec,
    outerHeight,
    y
  });

  const isStackedChart = updatedYScaleSpec.stacked;

  const defaultPalette = useDefaultPalette(data, isStackedChart);

  const getAxisBottom = () => {
    if (axisBottomSpec === null) {
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
              formatString: axisBottomSpec.formatString
            });
      }

      return undefined;
    };

    return {
      ...axisBottomSpec,
      format: axisBottomSpec.format ? axisBottomSpec.format : (value) => String(value),
      tickValues: getTickValues()
    };
  };

  const axisBottom = getAxisBottom();

  const colorsSpec = typeof colors === "function" ? colors : defaultPalette;
  const pointBorderColor = { from: "serieColor" };

  const overlayLayerProps = useMemo(
    () => ({
      xScale,
      areaOpacity: DEFAULT_AREA_OPACITY,
      outerHeight,
      outerWidth,
      margin,
      x,
      theme: chartTheme,
      linesAreaRectangle: {
        xStart: margin.left,
        xEnd: outerWidth - margin.right,
        yStart: margin.top,
        yEnd: outerHeight - margin.bottom,
        height: innerHeight,
        width: innerWidth
      }
    }),
    [chartTheme, innerHeight, innerWidth, margin, outerHeight, outerWidth, x, xScale]
  );

  return (
    <div
      style={{
        position: "relative",
        height: wrapperDimensions.height,
        width: wrapperDimensions.width
      }}
    >
      <SliceTooltipLayer
        sliceTooltip={({ slice }) => <ChartTooltip body={renderTooltipBody({ slice, stacked: isStackedChart })} />}
        xFormat={xFormat}
        yFormat={yFormat}
        data={data}
        colors={colorsSpec}
        series={series}
        pointColor={pointColor}
        pointBorderColor={pointBorderColor}
        enableSlices="x"
        layerProps={overlayLayerProps}
      />
      {overlayLayers.map(({ key, renderCanvasContent }) => (
        <CanvasLayer key={key} layerProps={overlayLayerProps} renderCanvasContent={renderCanvasContent} />
      ))}
      <ResponsiveLineCanvas
        data={data}
        animate={false}
        height={wrapperDimensions.height}
        width={wrapperDimensions.width}
        margin={margin}
        enableGridX={false}
        enableGridY={enableGridY}
        yScale={updatedYScaleSpec}
        xScale={xScaleSpec}
        colors={colorsSpec}
        enableArea
        areaOpacity={DEFAULT_AREA_OPACITY}
        axisLeft={axisLeft ? { ...axisLeft, tickValues: yTickValues, tickSize: 0 } : null}
        axisBottom={axisBottom}
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
        pointBorderColor={pointBorderColor}
        theme={chartTheme}
        lineWidth={1}
      />
    </div>
  );
};

const ResponsiveLine = ({
  data,
  isLoading,
  dataTestId,
  emptyMessageId = "noDataToDisplay",
  emptyMessageValues = {},
  style = {},
  ...rest
}) => {
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
                align="center"
                style={{
                  height: "100%",
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center"
                }}
              >
                <FormattedMessage id={emptyMessageId} values={emptyMessageValues} />
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

export default ResponsiveLine;

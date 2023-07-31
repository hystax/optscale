import React from "react";
import { scaleLinear, scaleOrdinal, scaleBand } from "d3-scale";
import CloudLabel from "components/CloudLabel";
import { isEmpty, sortObjects, getArithmeticMean, getElementsSum } from "utils/arrays";
import { EXPENSES_FILTERBY_TYPES } from "utils/constants";
import { remToPx } from "utils/fonts";
import { getTextWidth } from "utils/layouts";
import { idx } from "utils/objects";
import { getFontString } from "utils/strings";

// Empirically picked value, applied to all charts, flexible to separate between chart types
export const TICK_COUNT = 6;

/**
 * Get array of axis values
 *
 * @param { Array } lineChartData Line chart data
 * @param { String } dataKey Values store
 * @param { String } axisKey Values of which axis to take
 *
 * @returns {Array} array of values
 *
 * @example example usage of extractLineChartData function
 * // returns [218, 139]
 * extractLineChartData([
 *  {
 *    id:"expense",
 *    data: [{x: "August 2019", y: 218}, {x: "September 2019", y: 139}]
 *  }
 * ], "data", "y")
 */
export const extractLineChartData = (lineChartData, dataKey, axisKey) =>
  lineChartData.reduce((values, currentChartData) => {
    const currentLineValues = currentChartData[dataKey].reduce(
      (lineValues, pointValue) => lineValues.concat(pointValue[axisKey]),
      []
    );
    return values.concat(currentLineValues);
  }, []);

/**
 * Get array of summed axis values
 *
 * @param { Array } lineChartData Line chart data
 * @param { String } dataKey Values store
 * @param { String } axisKey Values of which axis to take
 *
 * @returns {Array} array of summed values
 *
 * @example example usage of extractStackedLineChartData function
 * // returns [130, 560]
 * extractLineChartData([
 *  {
 *    id:"Engineering",
 *    data: [{x: "1 week", y: 100}, {x: "2 week", y: 400}]
 *  },
 *  {
 *   id:"New Website",
 *   data: [{x: "1 week", y: 30}, {x: "2 week", y: 160}]
 * }
 * ], "data", "y")
 */
export const extractStackedLineChartData = (lineChartData, dataKey, axisKey) =>
  lineChartData.reduce((summedAxisData, data) => {
    const currentAxisData = data[dataKey].map((el) => el[axisKey]);
    if (summedAxisData.length === 0) {
      return currentAxisData;
    }
    return summedAxisData.map((el, index) => el + currentAxisData[index]);
  }, []);

/**
 * Get array of summed axis values
 *
 * @param { Array } barChartData Bar chart data
 * @param { Array } keys Bar chart keys
 *
 * @returns {Array} array of values
 *
 * @example example usage of extractBarChartValues function for non-stacked bar chart
 * // returns [3200, 1271]
 * extractBarChartValues([
 *  { index: "Last Month", month: "November", year: 2019, value: 3200 },
 *  { index: "Month-to-Date", month: "December", year: 2019, value: 1271 }
 * ], ["value"])
 *
 * @example example usage of extractBarChartValues function for stacked bar chart
 * // returns [260, 200]
 * extractBarChartValues([
 *  { period: "Forecast", Jira: 60, GitLab: 200 },
 *  { period: "Month-to-Date", Jira: 40, GitLab: 160 },
 * ], ["Jira", "GitLab"])
 */
export const extractBarChartValues = (barChartData, keys) =>
  barChartData.reduce(
    (chartValues, barValues) => {
      let positiveSum = 0;
      let negativeSum = 0;
      keys.forEach((key) => {
        if (barValues?.[key] && Math.sign(barValues[key]) === 1) {
          positiveSum += barValues[key];
        }
        if (barValues?.[key] && Math.sign(barValues[key]) === -1) {
          negativeSum += barValues[key];
        }
      });
      return {
        ...chartValues,
        positiveBandValues: [...chartValues.positiveBandValues, positiveSum],
        negativeBandValues: [...chartValues.negativeBandValues, negativeSum]
      };
    },
    { positiveBandValues: [], negativeBandValues: [] }
  );

export const getColorScale = (palette) => {
  const scale = scaleOrdinal(palette);
  return (value) => scale(value);
};

export const getColorsMapByIds = ({ data, key = "name", uniqueDataIdentifier = "id", colors }) => {
  const colorScale = getColorScale(colors);
  return Object.fromEntries(data.map((value) => [value[key], colorScale(value[uniqueDataIdentifier])]));
};

export const getColorsMap = (values, colors) => {
  const colorScale = getColorScale(colors);
  return Object.fromEntries(values.map((value) => [value, colorScale(value)]));
};

export const getMaxAndMinBandValues = (data, keys) => {
  const { positiveBandValues, negativeBandValues } = extractBarChartValues(data, keys);

  return {
    maxBandValue: Math.max(...positiveBandValues),
    minBandValue: Math.min(...negativeBandValues)
  };
};

export const addEntityIconToTooltipKey = (text, details, entityName) => {
  let textWithIcon;
  if (details.type) {
    textWithIcon = {
      [EXPENSES_FILTERBY_TYPES.CLOUD]: <CloudLabel type={details.type} label={text} />
    }[entityName];
  }
  return textWithIcon || text;
};

const getTickValues = ({ range, minValue, maxValue, ticksCount }) =>
  scaleLinear().rangeRound(range).domain([minValue, maxValue]).ticks(ticksCount);

export const getScale = (tickValues) => (tickValues.length === 1 ? 0 : tickValues[1] - tickValues[0]);

const getTicks = ({ minValue, maxValue, range, ticksCount, minMaxTicksEqualToMinMaxValues = false }) => {
  // «getTickValues» returns array with 1 element if «minValue» === «maxValue»
  const tickValues = getTickValues({ range, minValue, maxValue, ticksCount });

  if (minMaxTicksEqualToMinMaxValues) {
    return {
      tickValues,
      gridValues: tickValues,
      maxValue,
      minValue
    };
  }

  const scale = getScale(tickValues);

  const newMaxValue = maxValue === 0 ? maxValue : maxValue + scale;
  const newMinValue = minValue === 0 ? minValue : minValue - scale;

  const newTickValues = getTickValues({ range, minValue: newMinValue, maxValue: newMaxValue, ticksCount });
  const newScale = getScale(newTickValues);

  let maxTick = Math.max(...newTickValues);
  let minTick = Math.min(...newTickValues);

  if (maxTick !== 0 && maxTick <= maxValue) {
    newTickValues.push(maxTick + newScale);
    maxTick += newScale;
  }

  if (minTick !== 0 && minTick >= minValue) {
    newTickValues.push(minTick - newScale);
    minTick -= newScale;
  }

  // TODO - why do we need the same value assigned to different variables ?
  return {
    tickValues: newTickValues,
    gridValues: newTickValues,
    maxValue: maxTick,
    minValue: minTick
  };
};

export const getBarTicks = ({ height, layout, ticksCount, maxValue, minValue = 0, minMaxTicksEqualToMinMaxValues }) => {
  const range = layout === "vertical" ? [height, minValue] : [minValue, height];
  return getTicks({ minValue, maxValue, range, ticksCount, minMaxTicksEqualToMinMaxValues });
};

export const getLineYTicks = ({ yMin, yMax, height, ticksCount, minMaxTicksEqualToMinMaxValues }) => {
  const range = [height, 0];

  return getTicks({ minValue: yMin, maxValue: yMax, range, ticksCount, minMaxTicksEqualToMinMaxValues });
};

/**
 * @description By default, we always define the details object in the chart data. The purpose of this function is to define an additional information based on user needs
 * @param {Object} details - additional information about chart content. If details ia a function it will recieve item as a parameter
 * @param {Object} item - current item from the source array
 * @returns {Object} defined custom details
 */
const getCustomDetails = (details, item) => (typeof details === "function" ? details(item) : details);

/**
 *
 * @param {Object} options - the options that defines pie chart settings
 * @param {Array} options.colors - the set of colors
 * @param {Array} options.sourceData - the raw data
 * @param {string} options.idField - field (in the raw data) that represents an "id" key in the pie data
 * @param {string} options.valueField - field (in the raw data) that represents a "value" key in the pie data
 * @param {Object} options.sortSettings - data sort setting. By default, type is "desc" and field is "valueField"
 * @param {Function} options.onClick - onClick event handler
 * @param {(boolean|Function)} options.shouldApplyHoverStyles - identify if hover styles should be applied. Function accepts section data and event object and should return true|false
 * @param {(Function|Object)} options.customDetails - pie data always has "details" propery. This function|object is used to define extra details. If the customDetails is a function then it should always return an object.
 * @see https://nivo.rocks/pie/ - for more information about data structure, themes, events, etc
 */
export const getPieChartOptions = ({
  colors,
  sourceData,
  idField = "id",
  valueField = "value",
  labelField = "label",
  sortSettings,
  onClick,
  shouldApplyHoverStyles,
  customDetails = {},
  tooltipIcon
}) => {
  const defaultSortSettings = {
    type: "desc",
    field: valueField
  };
  const computedSortSettings = { ...defaultSortSettings, ...sortSettings };
  const colorScale = getColorScale(colors);
  const pieDataAndPalette = sortObjects({
    array: sourceData,
    type: computedSortSettings.type,
    field: computedSortSettings.field
  }).reduce(
    (result, item) => {
      const { [idField]: id, [labelField]: label } = item;
      const value = (Array.isArray(valueField) ? idx(valueField, item) : item[valueField]) || 0;
      const color = colorScale(id);
      if (value !== 0) {
        return {
          ...result,
          palette: [...result.palette, color],
          data: [
            ...result.data,
            {
              id,
              value,
              label,
              details: {
                ...item,
                ...getCustomDetails(customDetails, item)
              }
            }
          ]
        };
      }
      return result;
    },
    { palette: [], data: [] }
  );

  return {
    ...pieDataAndPalette,
    onClick,
    shouldApplyHoverStyles,
    tooltipIcon
  };
};

export const getBandDetailsKey = (value) => `${value}_DETAILS`;

/**
 *
 * @param {Object} sourceData
 * object in format:
 * ```
 * {
 *   [indexBy]: [
 *     {
 *       [keyField]: val,
 *       [keyValue]: val,
 *       ...rest
 *     }
 *   ],
 *   [indexBy]: [
 *     {
 *       [keyField]: val,
 *       [keyValue]: val,
 *       ...rest}
 *   ],
 *   ...
 * }
 * ```
 *
 */
export const getBarChartDataAndKeys = ({
  keyField = "name",
  keyValue = "value",
  indexBy = "id",
  sourceData,
  sortType = "desc",
  formatIndexByValue
}) => {
  let keys = {};
  const data = Object.entries(sourceData).map(([indexByValue, values]) => {
    const indexByDefinition = {
      [indexBy]: typeof formatIndexByValue === "function" ? formatIndexByValue(indexByValue) : indexByValue
    };

    if (!Array.isArray(values) || isEmpty(values)) return indexByDefinition;

    const chartValues = values.reduce((result, value) => {
      keys = { ...keys, [value[keyField]]: keys[value[keyField]] + value[keyValue] || value[keyValue] };
      return {
        ...result,
        [value[keyField]]: value[keyValue],
        [getBandDetailsKey(value[keyField])]: {
          ...value
        }
      };
    }, {});
    return {
      ...indexByDefinition,
      ...chartValues
    };
  });
  const filteredKeys = Object.keys(keys)
    // exclude keys that has zero (0) values in order to save spacing between bands in the stacked charts
    .filter((key) => keys[key])
    // sort keys in order to determine bands order
    .sort((a, b) => (sortType === "desc" ? keys[b] - keys[a] : keys[a] - keys[b]));

  return {
    keys: filteredKeys,
    data
  };
};

export const getExpensesPieChartOptions = ({
  sourceArray,
  onClick,
  shouldApplyHoverStyles,
  customDetails,
  tooltipIcon,
  colors
}) =>
  getPieChartOptions({
    colors,
    sourceData: [...sourceArray],
    idField: "id",
    valueField: "total",
    labelField: "name",
    sortSettings: {
      field: "total"
    },
    onClick,
    shouldApplyHoverStyles,
    customDetails,
    tooltipIcon
  });

export const getTickLabelWidth = (label, font) => {
  // TODO - calculate average character size based on font
  const minSpaceBetweenLabels = 6;

  return minSpaceBetweenLabels + getTextWidth(label, font);
};

const isCollapse = (tickA, tickB) => {
  const { coordinate: tickACoordinate, width: tickAWidth } = tickA;
  const { coordinate: tickBCoordinate, width: tickBWidth } = tickB;

  const distance = Math.abs(tickACoordinate - tickBCoordinate);

  return (tickAWidth + tickBWidth) / 2 >= distance;
};

export const calculateTickValues = (xValues) => {
  if (xValues.length <= 1) return xValues.map(({ value }) => value);

  let lastAdded = 0;

  return xValues.reduce(
    (allTickValues, xValue, index) => {
      if (isCollapse(xValue, xValues[lastAdded])) {
        return allTickValues;
      }

      lastAdded = index;
      return [...allTickValues, xValue.value];
    },
    [xValues[0].value]
  );
};

const getBottomAxisFontSettings = (font) => ({
  // We usually work with 'rem' for font sizes, but pixels are used for calculations, so here we convert rem to px
  fontSize: font.fontSize.toString().includes("rem") ? remToPx(parseFloat(font.fontSize)) : parseInt(font.fontSize, 10),
  fontFamily: font.fontFamily
});

export const getBarChartBottomTickValues = ({ data, indexBy, padding, font, innerWidth }) => {
  const domain = data.map((el) => el[indexBy]);
  const range = [0, innerWidth];

  const scale = scaleBand().range(range).domain(domain).padding(padding);

  const fontSettings = getBottomAxisFontSettings(font);

  return calculateTickValues(
    domain.map((xValue) => ({
      value: xValue,
      width: getTickLabelWidth(xValue, getFontString(fontSettings.fontSize, fontSettings.fontFamily, "px")),
      coordinate: scale(xValue)
    }))
  );
};

export const getLineChartBottomTickValues = ({ x, scale, font, formatString }) => {
  const fontSettings = getBottomAxisFontSettings(font);

  return calculateTickValues(
    x.all.map((xValue) => {
      const formattedXValue = typeof formatString === "function" ? formatString(xValue) : xValue;

      return {
        value: xValue,
        width: getTickLabelWidth(formattedXValue, getFontString(fontSettings.fontSize, fontSettings.fontFamily, "px")),
        coordinate: scale(xValue)
      };
    })
  );
};

/**
 * Calculate width of the occupied space
 *
 * @param { number } wrapperWidth - Width of the container
 * @param { Object } margin - Margin settings (left, right, top, bottom)
 * @param { string } [layout=vertical] - Chart layout (vertical/horizontal)
 *
 * @description
 * Get width of the occupied space:
 *
 * vertical layout: wrapperWidth - (leftMargin + rightMargin)
 *
 * horizontal layout: wrapperWidth - (topMargin + bottomMargin)
 *
 * @returns Width of the the occupied space
 */
export const getChartWidth = (wrapperWidth, margin, layout = "vertical") => {
  if (wrapperWidth === 0) {
    return 0;
  }
  const { left = 0, right = 0, top = 0, bottom = 0 } = margin;
  return layout === "vertical" ? wrapperWidth - (left + right) : wrapperWidth - (top + bottom);
};

export const getLineValues = (lineData) => lineData.map(({ y }) => y);

export const getAverageLineValue = (lineData) => {
  const lineValues = getLineValues(lineData);
  return getArithmeticMean(lineValues);
};

export const getTotalLineValue = (lineData) => {
  const lineValues = getLineValues(lineData);
  return getElementsSum(lineValues);
};

export const AXIS_FORMATS = Object.freeze({
  MONEY: "money",
  RAW: "raw",
  PERCENTAGE: "percentage"
});

export const getScaledCanvasContext = (canvasElement, { width, height }) => {
  const ctx = canvasElement.getContext("2d");

  /* eslint-disable no-return-assign, no-param-reassign */
  canvasElement.width = width * window.devicePixelRatio;
  canvasElement.height = height * window.devicePixelRatio;
  canvasElement.style.width = `${width}px`;
  canvasElement.style.height = `${height}px`;
  /* eslint-enable no-return-assign, no-param-reassign */

  ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

  return ctx;
};

export const renderCanvasLine = (
  ctx,
  {
    points = [],
    originRelativeToCanvas = {
      x: 0,
      y: 0
    },
    strokeStyle,
    fillStyle,
    lineWidth = 2,
    dotRadius = 3
  } = {}
) => {
  ctx.save();

  ctx.strokeStyle = strokeStyle;
  ctx.fillStyle = fillStyle;

  ctx.lineWidth = lineWidth;
  ctx.lineJoin = "round";
  ctx.lineCap = "round";

  // line
  const { x: firstX, y: firstY } = points[0];
  ctx.beginPath();
  ctx.moveTo(firstX, firstY);
  points.forEach(({ x, y }) => ctx.lineTo(x, y));
  ctx.stroke();

  const [lastPoint] = points.slice(-1);
  const { x: lastX, y: lastY } = lastPoint;

  // dot (color is taken from current image data)
  const { data: pixel } = ctx.getImageData(
    window.devicePixelRatio * (lastX + originRelativeToCanvas.x),
    window.devicePixelRatio * (lastY + originRelativeToCanvas.y),
    1,
    1
  );

  const pixelColorRGBA = `rgba(${pixel[0]}, ${pixel[1]}, ${pixel[2]}, ${pixel[3] / 255})`;

  ctx.beginPath();
  ctx.fillStyle = pixelColorRGBA;
  ctx.arc(lastX, lastY, dotRadius, 0, Math.PI * 2, true);
  ctx.fill();

  ctx.restore();
};

import React from "react";
import { Box } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { ResponsivePie } from "@nivo/pie";
import PropTypes from "prop-types";
import ChartTooltip from "components/ChartTooltip";
import FormattedMoney from "components/FormattedMoney";
import { useChartHoverStyles } from "hooks/useChartHoverStyles";
import { DEFAULT_CHART_BORDER_WIDTH, FORMATTED_MONEY_TYPES } from "utils/constants";
import { isEmpty } from "utils/objects";

const CenteredMetric = ({ dataWithArc, centerX, centerY }) => {
  const total = dataWithArc.reduce((accumulator, { value }) => accumulator + value, 0);

  return (
    <text x={centerX} y={centerY} textAnchor="middle" dominantBaseline="central">
      <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={total} />
    </text>
  );
};

const getColor = (colorsMap) => (pie) => colorsMap[pie.label];

const PieChart = ({
  data,
  colorsMap = {},
  palette,
  style = {},
  onClick,
  renderTooltipBody,
  borderWidth = DEFAULT_CHART_BORDER_WIDTH,
  shouldApplyHoverStyles = true
}) => {
  const { height = 30, margin = { top: 10 } } = style;
  const theme = useTheme();

  const chartPalette = palette || theme.palette.chart;

  const [wrapperClass, addHoverClass, removeHoverClass] = useChartHoverStyles({ borderWidth });

  const applyHoverStyles = (node, event) => {
    if (onClick) {
      const shouldApply =
        typeof shouldApplyHoverStyles === "function" ? shouldApplyHoverStyles(node, event) : shouldApplyHoverStyles;
      if (shouldApply) {
        addHoverClass(event.target);
      }
    }
  };

  const removeHoverStyles = (node, event) => {
    if (onClick) {
      removeHoverClass(event.target);
    }
  };

  return (
    <Box className={wrapperClass} height={theme.spacing(height)}>
      <ResponsivePie
        data={data}
        layers={["arcs", CenteredMetric]}
        margin={margin}
        colors={isEmpty(colorsMap) ? chartPalette : getColor(colorsMap)}
        enableRadialLabels={false}
        enableSliceLabels={false}
        borderWidth={borderWidth}
        innerRadius={0.7}
        onMouseEnter={(node, event) => applyHoverStyles(node, event)}
        onMouseLeave={(node, event) => removeHoverStyles(node, event)}
        borderColor={{ from: "color", modifiers: [["darker", 1.3]] }}
        tooltip={({ datum }) => <ChartTooltip body={renderTooltipBody(datum)} />}
        onClick={onClick}
        animate={false}
        theme={{
          tooltip: {
            zIndex: theme.zIndex.tooltip
          }
        }}
      />
    </Box>
  );
};

PieChart.propTypes = {
  data: PropTypes.array.isRequired,
  palette: PropTypes.array,
  height: PropTypes.number,
  style: PropTypes.object,
  colorsMap: PropTypes.object,
  onClick: PropTypes.func,
  shouldApplyHoverStyles: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
  renderTooltipBody: PropTypes.func,
  borderWidth: PropTypes.number
};

export default PieChart;

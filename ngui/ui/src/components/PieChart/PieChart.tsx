import { Box } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { ResponsivePie } from "@nivo/pie";
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
  // Consume full width of a container by default. theme.spacing seems to be working correctly with percentage as well.
  const { height = 30, width = "100%", margin = { top: 10 } } = style;
  const theme = useTheme();

  const chartPalette = palette || theme.palette.chart;

  const [wrapperClass, addHoverClass, removeHoverClass] = useChartHoverStyles({
    borderWidth,
    isClickable: typeof onClick === "function"
  });

  const applyHoverStyles = (node, event) => {
    const shouldApply =
      typeof shouldApplyHoverStyles === "function" ? shouldApplyHoverStyles(node, event) : shouldApplyHoverStyles;
    if (shouldApply) {
      addHoverClass(event.target);
    }
  };

  const removeHoverStyles = (node, event) => {
    removeHoverClass(event.target);
  };

  return (
    <Box className={wrapperClass} height={theme.spacing(height)} width={theme.spacing(width)}>
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

export default PieChart;

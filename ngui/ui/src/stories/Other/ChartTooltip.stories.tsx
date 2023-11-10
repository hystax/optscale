import Box from "@mui/material/Box";
import { useTheme } from "@mui/material/styles";
import { ResponsiveBar } from "@nivo/bar";
import ChartTooltip from "components/ChartTooltip";
import { KINDS } from "stories";

export default {
  title: `${KINDS.OTHER}/ChartTooltip`,
  argTypes: {
    title: { name: "Title", control: "text", defaultValue: "Title" },
    text: { name: "Text", control: "text", defaultValue: "Text" },
    value: { name: "Value", control: "text", defaultValue: "Value" },
    isBoldTitle: { name: "Bold title", control: "boolean", defaultValue: false },
    isBoldText: { name: "Bold text", control: "boolean", defaultValue: false },
    isBoldValue: { name: "Bold value", control: "boolean", defaultValue: false }
  }
};

const chartData = [
  { date: 1606780799, total: 87.07, expensesPeriod: "thisMonthForecast", index: "Hover your mouse to see the tooltip" }
];

export const basic = (args) => {
  const theme = useTheme();
  const colors = theme.palette.chart;

  return (
    <Box height="20rem" width="20rem">
      <ResponsiveBar
        data={chartData}
        animate={false}
        keys={["total"]}
        indexBy="index"
        colors={colors}
        borderWidth={1}
        borderColor={{ from: "color", modifiers: [["darker", 1.3]] }}
        tooltip={() => (
          <ChartTooltip
            title={args.title}
            boldTitle={args.boldTitle}
            text={args.text}
            boldText={args.boldText}
            value={args.value}
            boldValue={args.boldValue}
          />
        )}
        margin={{
          top: 10,
          bottom: 50,
          right: 50,
          left: 75
        }}
        padding={0.7}
      />
    </Box>
  );
};

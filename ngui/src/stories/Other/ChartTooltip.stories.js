import React from "react";
import Box from "@mui/material/Box";
import { ResponsiveBar } from "@nivo/bar";
import { text, boolean } from "@storybook/addon-knobs";
import { MONO_CHART_PALETTE } from "theme";
import ChartTooltip from "components/ChartTooltip";
import { useTheme } from "@mui/material/styles";
import { KINDS } from "stories";

export default {
  title: `${KINDS.OTHER}/ChartTooltip`
};

const chartData = [
  { date: 1606780799, total: 87.07, expensesPeriod: "thisMonthForecast", index: "Hover your mouse to see the tooltip" }
];

export const basic = () => {
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
            title={text("title", "Title")}
            boldTitle={boolean("bold title", false)}
            text={text("text", "Title")}
            boldText={boolean("bold text", false)}
            value={text("value", "value")}
            boldValue={boolean("bold value", false)}
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

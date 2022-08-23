import React, { useState } from "react";
import BarChart from "components/BarChart";
import { number, select, boolean, button } from "@storybook/addon-knobs";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/BarChart`
};

const chartBasicData = [
  {
    month: "January",
    year: 2019,
    value: 11
  },
  {
    month: "February",
    year: 2020,
    value: 8
  },
  {
    month: "March",
    year: 2020,
    value: 5
  },
  {
    month: "April",
    year: 2020,
    value: 5
  },
  {
    month: "May",
    year: 2020,
    value: 5
  }
];

const layoutOptions = {
  horizontal: "horizontal",
  vertical: "vertical"
};

export const basic = () => (
  <BarChart data={chartBasicData} keys={["value"]} indexBy="month" fieldTooltipText={["data", "month"]} />
);

export const stacked = () => {
  return (
    <BarChart
      data={[
        {
          date: "11/12/20",
          EK_azure_connection: 3.6875021912,
          AWS: 17.7631119176
        },
        {
          date: "11/13/20",
          EK_azure_connection: 3.5642907612,
          AWS: 21.5972734967
        },
        {
          date: "11/14/20",
          EK_azure_connection: 3.5642908612,
          AWS: 12.011647146
        },
        {
          date: "11/15/20",
          EK_azure_connection: 3.5642901412,
          AWS: 12.013647071
        },
        {
          date: "11/16/20",
          EK_azure_connection: 3.5261599399,
          AWS: 20.1823180084
        },
        {
          date: "11/17/20",
          EK_azure_connection: 3.5554594268999997,
          AWS: 25.673406494
        },
        {
          date: "11/18/20",
          AWS: 12.716525231,
          EK_azure_connection: 2.503647303
        }
      ]}
      keys={["AWS", "EK_azure_connection"]}
      indexBy={"date"}
    />
  );
};

const WithKnobsBarChart = () => {
  const months = ["January", "February", "March", "April", "May"];
  const year = 2020;
  const defaultMaxValue = 10;

  const generateDataSet = (maxValue = defaultMaxValue) =>
    months.map((month) => ({
      month,
      year,
      value: Math.random() * maxValue
    }));

  const [data, setData] = useState(generateDataSet());

  button("Generate data", () => {
    const maxValue = number("Max value", defaultMaxValue);
    setData(generateDataSet(maxValue));
  });

  return (
    <BarChart
      layout={select("layout", layoutOptions, "vertical")}
      data={data}
      keys={["value"]}
      markers={
        boolean("Render markers", true)
          ? {
              alwaysDisplay: boolean("Always display markers", true),
              value: number("Markers value", 12),
              format: "USD"
            }
          : {}
      }
      indexBy="month"
      fieldTooltipText={["data", "month"]}
    />
  );
};

export const withKnobs = () => <WithKnobsBarChart />;

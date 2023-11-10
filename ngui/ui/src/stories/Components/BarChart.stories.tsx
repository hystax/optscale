import BarChart from "components/BarChart";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/BarChart`,
  argTypes: {
    marker: { name: "Marker value", control: "number", defaultValue: 12 },
    layout: {
      name: "Layout",
      control: "select",
      options: ["horizontal", "vertical"],
      defaultValue: "vertical"
    },
    withMarker: { name: "With markers", control: "boolean", defaultValue: true },
    alwaysWithMarker: { name: "Always with markers", control: "boolean", defaultValue: true }
  }
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

export const basic = () => (
  <BarChart data={chartBasicData} keys={["value"]} indexBy="month" fieldTooltipText={["data", "month"]} />
);

export const stacked = () => (
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

const WithKnobsBarChart = (args) => {
  const months = ["January", "February", "March", "April", "May"];
  const year = 2020;

  const data = months.map((month) => ({
    month,
    year,
    value: Math.random() * 10
  }));

  return (
    <BarChart
      layout={args.layout}
      data={data}
      keys={["value"]}
      markers={
        args.withMarker
          ? {
              alwaysDisplay: args.alwaysWithMarker,
              value: args.marker,
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

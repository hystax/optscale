import LineChart from "components/LineChart";

export default {
  component: LineChart,
  argTypes: {
    data: {
      name: "Data",
      control: "select",
      options: [
        {
          id: "Item 1",
          data: [
            { x: "01/03/2021", y: 100 },
            { x: "01/04/2021", y: 100 },
            { x: "01/05/2021", y: 100 },
            { x: "01/06/2021", y: 100 },
            { x: "01/07/2021", y: 100 }
          ]
        },
        {
          id: "Item 2",
          data: [
            { x: "01/03/2021", y: 200 },
            { x: "01/04/2021", y: 200 },
            { x: "01/05/2021", y: 200 },
            { x: "01/06/2021", y: 200 },
            { x: "01/07/2021", y: 200 }
          ]
        },
        {
          id: "Item 3",
          data: [
            { x: "01/03/2021", y: 300 },
            { x: "01/04/2021", y: 300 },
            { x: "01/05/2021", y: 300 },
            { x: "01/06/2021", y: 300 },
            { x: "01/07/2021", y: 300 }
          ]
        }
      ],
      defaultValue: {}
    },
    stacked: { name: "Stacked", control: "boolean", defaultValue: true },
    isLoading: { name: "Loading", control: "boolean", defaultValue: false }
  }
};

export const withKnobs = (args) => <LineChart data={args.data} stacked={args.stacked} isLoading={args.isLoading} />;

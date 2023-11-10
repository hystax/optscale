import PieChart from "components/PieChart";
import PieChartLoader from "components/PieChartLoader";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/PieChartLoader`,
  argTypes: {
    height: { name: "Height", control: "number", defaultValue: 30 }
  }
};

const data = [
  {
    id: "sass",
    label: "sass",
    value: 513
  },
  {
    id: "elixir",
    label: "elixir",
    value: 216
  },
  {
    id: "rust",
    label: "rust",
    value: 11
  },
  {
    id: "css",
    label: "css",
    value: 397
  },
  {
    id: "javascript",
    label: "javascript",
    value: 94
  }
];

export const defaultHeight = () => (
  <div>
    <PieChartLoader />
    <PieChart data={data} />
  </div>
);

export const withKnobs = (args) => {
  const { height } = args;
  return (
    <div>
      <PieChartLoader height={height} />
      <PieChart data={data} style={{ height }} />
    </div>
  );
};

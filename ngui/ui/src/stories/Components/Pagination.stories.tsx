import Pagination from "components/Table/components/Pagination";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Pagination`,
  argTypes: {
    position: {
      name: "Position",
      control: "select",
      options: ["right", "center", "left"],
      defaultValue: "right"
    },
    count: { name: "Count", control: "number", defaultValue: 2 },
    limit: { name: "Limit", control: "number", defaultValue: 1 }
  }
};

export const basic = () => <Pagination paginationHandler={(page) => console.log(page)} count={5} limit={1} />;

export const withKnobs = (args) => (
  <Pagination paginationHandler={(page) => console.log(page)} position={args.position} count={args.count} limit={args.limit} />
);

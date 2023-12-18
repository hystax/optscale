import TableLoader from "components/TableLoader";

export default {
  component: TableLoader,
  argTypes: {
    columnCount: { name: "Column count", control: "number", defaultValue: 1 },
    showHeader: { name: "Show header", control: "boolean", defaultValue: true }
  }
};

export const withKnobs = (args) => <TableLoader columnsCounter={args.columnCount} showHeader={args.showHeader} />;

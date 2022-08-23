import React from "react";
import { number, boolean } from "@storybook/addon-knobs";
import TableLoader from "components/TableLoader";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/TableLoader`
};

export const withKnobs = () => (
  <TableLoader columnsCounter={number("Number of columns", 1)} showHeader={boolean("Show header", true)} />
);

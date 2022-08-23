import React from "react";
import { number, select } from "@storybook/addon-knobs";
import Pagination from "components/Table/Pagination";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Pagination`
};

export const basic = () => <Pagination paginationHandler={(page) => console.log(page)} count={5} limit={1} />;

export const withKnobs = () => (
  <Pagination
    paginationHandler={(page) => console.log(page)}
    position={select("position", { right: "right", center: "center", left: "left" }, "right")}
    count={number("count", 2)}
    limit={number("limit", 1)}
  />
);

import React, { useState } from "react";
import LineChart from "components/LineChart";
import { boolean, object } from "@storybook/addon-knobs";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/LineChart`
};

const data = [
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
];

export const withKnobs = () => (
  <LineChart data={object("data", data)} stacked={boolean("stacked", true)} isLoading={boolean("isLoading", false)} />
);

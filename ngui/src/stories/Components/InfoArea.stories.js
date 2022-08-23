import React from "react";
import { number } from "@storybook/addon-knobs";
import InfoArea from "components/Table/InfoArea";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/InfoArea`
};

export const basic = () => (
  <InfoArea selectedRowsCount={10} showCounters hideTotal={false} totalNumber={5050} rowsLength={20} />
);

export const displayedFromTo = () => (
  <InfoArea
    selectedRowsCount={10}
    showCounters
    hideTotal={false}
    totalNumber={5050}
    rowsLength={20}
    pageSize={20}
    pagesNum={5000 / 20}
    currentPage={0}
  />
);

export const withKnobs = () => {
  const displayed = { count: number("count", 1) };

  return <InfoArea showCounters hideTotal rowsLength={displayed.count} />;
};

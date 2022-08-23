import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import { millisecondsToSeconds } from "utils/datetime";
import RegionExpenses from "./RegionExpenses";

const firstDateRangePoint = millisecondsToSeconds(+new Date());
const lastDateRangePoint = millisecondsToSeconds(+new Date());

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider
      state={{
        rangeDates: {}
      }}
    >
      <RegionExpenses
        expenses={{}}
        applyFilter={() => {}}
        startDateTimestamp={firstDateRangePoint}
        endDateTimestamp={lastDateRangePoint}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});

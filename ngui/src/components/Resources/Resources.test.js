import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import { millisecondsToSeconds } from "utils/datetime";
import Resources from "./Resources";

const firstDateRangePoint = millisecondsToSeconds(+new Date());
const lastDateRangePoint = millisecondsToSeconds(+new Date());

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Resources
        filterValues={{}}
        startDateTimestamp={firstDateRangePoint}
        endDateTimestamp={lastDateRangePoint}
        requestParams={{}}
        filters={{}}
        entities={{}}
        totalExpenses={0}
        fromMainMenu={false}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});

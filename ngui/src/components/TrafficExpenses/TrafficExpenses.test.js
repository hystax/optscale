import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import { millisecondsToSeconds } from "utils/datetime";
import TrafficExpenses from "./TrafficExpenses";

const firstDateRangePoint = millisecondsToSeconds(+new Date());
const lastDateRangePoint = millisecondsToSeconds(+new Date());

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider
      state={{
        rangeDates: {}
      }}
    >
      <TrafficExpenses
        expenses={{}}
        applyFilter={() => {}}
        startDateTimestamp={firstDateRangePoint}
        endDateTimestamp={lastDateRangePoint}
      />
    </TestProvider>
  );
  root.unmount();
});

import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import { getCurrentTimeInMsec, addDays } from "utils/datetime";
import RangePicker from "./RangePicker";

const today = getCurrentTimeInMsec();
const nextWeek = addDays(today, 7);

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <RangePicker initialDateRange={{ startDate: today, endDate: nextWeek }} onChange={vi.fn} />
    </TestProvider>
  );
  root.unmount();
});

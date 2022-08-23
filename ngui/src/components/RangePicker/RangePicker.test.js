import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import { getCurrentTimeInMsec, addDays } from "utils/datetime";
import RangePicker from "./RangePicker";

const today = getCurrentTimeInMsec();
const nextWeek = addDays(today, 7);

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <RangePicker initialDateRange={{ startDate: today, endDate: nextWeek }} onChange={jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});

import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import { millisecondsToSeconds } from "utils/datetime";
import RangePickerForm from "./RangePickerForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <RangePickerForm
        initialStartDateValue={millisecondsToSeconds(+new Date())}
        initialEndDateValue={millisecondsToSeconds(+new Date())}
        onApply={jest.fn}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});

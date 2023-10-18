import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import { millisecondsToSeconds } from "utils/datetime";
import RangePickerForm from "./RangePickerForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <RangePickerForm
        initialStartDateValue={millisecondsToSeconds(+new Date())}
        initialEndDateValue={millisecondsToSeconds(+new Date())}
        onApply={vi.fn}
      />
    </TestProvider>
  );
  root.unmount();
});

import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Month from "./Month";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Month
        value={new Date()}
        dateRange={{ startDate: new Date(), endDate: new Date() }}
        minDate={new Date()}
        maxDate={new Date()}
        helpers={{ inHoverRange: () => {} }}
        userBounds={{ minDate: 0, maxDate: 0 }}
      />
    </TestProvider>
  );
  root.unmount();
});

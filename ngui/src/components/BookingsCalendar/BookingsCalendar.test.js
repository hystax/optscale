import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import BookingsCalendar from "./BookingsCalendar";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <BookingsCalendar environments={[]} />
    </TestProvider>
  );
  root.unmount();
});

import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import UpcomingBooking from "./UpcomingBooking";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <UpcomingBooking employeeName="A" acquiredSince={0} releasedAt={1} />
    </TestProvider>
  );
  root.unmount();
});

import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import EventsOverviewList from "./EventsOverviewList";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <EventsOverviewList events={[]} />
    </TestProvider>
  );
  root.unmount();
});

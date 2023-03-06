import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ArchivedResourcesCountBarChart from "./ArchivedResourcesCountBarChart";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ArchivedResourcesCountBarChart onSelect={jest.fn} breakdown={{}} />
    </TestProvider>
  );
  root.unmount();
});

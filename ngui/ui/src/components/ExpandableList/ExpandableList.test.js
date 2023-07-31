import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ExpandableList from "./ExpandableList";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ExpandableList items={[]} render={() => {}} />
    </TestProvider>
  );
  root.unmount();
});

import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import AvailablePoolSelector from "./AvailablePoolSelector";

const pools = [
  {
    id: "id",
    name: "Name",
    test: 123
  }
];

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <AvailablePoolSelector pools={pools} />
    </TestProvider>
  );
  root.unmount();
});

import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import EnvironmentsCard from "./EnvironmentsCard";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <EnvironmentsCard environments={[]} />
    </TestProvider>
  );
  root.unmount();
});

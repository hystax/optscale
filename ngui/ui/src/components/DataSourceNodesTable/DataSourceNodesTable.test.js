import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import DataSourceNodesTable from "./DataSourceNodesTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <DataSourceNodesTable nodes={[]} />
    </TestProvider>
  );
  root.unmount();
});

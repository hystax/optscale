import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import TableLoader from "./TableLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <TableLoader columnsCounter={3} />
    </TestProvider>
  );
  root.unmount();
});

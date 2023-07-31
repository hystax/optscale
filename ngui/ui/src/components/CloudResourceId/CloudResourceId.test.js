import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import CloudResourceId from "./CloudResourceId";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CloudResourceId resourceId="" cloudResourceIdentifier="" />
    </TestProvider>
  );
  root.unmount();
});

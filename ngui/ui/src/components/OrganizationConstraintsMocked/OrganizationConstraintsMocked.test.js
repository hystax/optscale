import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import OrganizationConstraintsMocked from "./OrganizationConstraintsMocked";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <OrganizationConstraintsMocked actionBarDefinition={{}} />
    </TestProvider>
  );
  root.unmount();
});

import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import OrganizationOptions from "./OrganizationOptions";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <OrganizationOptions expandedOption="" requestedOption="" value={{}} handleExpand={() => {}} options={[]} />
    </TestProvider>
  );
  root.unmount();
});

import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Jira from "./Jira";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Jira totalEmployees={0} connectedEmployees={0} isCurrentEmployeeConnectedToJira connectedWorkspaces={[]} />
    </TestProvider>
  );
  root.unmount();
});

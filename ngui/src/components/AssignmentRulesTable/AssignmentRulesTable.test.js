import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import AssignmentRulesTable from "./AssignmentRulesTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <AssignmentRulesTable assignmentRules={[]} organizationId="" entities={{}} />
    </TestProvider>
  );
  root.unmount();
});

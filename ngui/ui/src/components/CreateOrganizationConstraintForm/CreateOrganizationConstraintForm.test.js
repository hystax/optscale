import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import CreateOrganizationConstraintForm from "./CreateOrganizationConstraintForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CreateOrganizationConstraintForm onSubmit={vi.fn} types={[]} navigateAway={vi.fn} />
    </TestProvider>
  );
  root.unmount();
});

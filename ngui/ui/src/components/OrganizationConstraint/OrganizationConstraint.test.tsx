import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import OrganizationConstraint from "./OrganizationConstraint";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <OrganizationConstraint actionBarTitleDefinition={{}} actionBarBreadcrumbsDefinition={[]} constraint={{}} />
    </TestProvider>
  );
  root.unmount();
});

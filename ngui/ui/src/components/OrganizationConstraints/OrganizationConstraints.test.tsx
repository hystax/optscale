import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import OrganizationConstraints from "./OrganizationConstraints";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <OrganizationConstraints actionBarDefinition={{}} constraints={[]} addButtonLink="" />
    </TestProvider>
  );
  root.unmount();
});

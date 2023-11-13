import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import DeleteOrganizationOption from "./DeleteOrganizationOption";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <DeleteOrganizationOption name="" />
    </TestProvider>
  );
  root.unmount();
});

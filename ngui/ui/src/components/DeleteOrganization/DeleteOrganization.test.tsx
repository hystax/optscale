import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import DeleteOrganization from "./DeleteOrganization";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <DeleteOrganization />
    </TestProvider>
  );
  root.unmount();
});

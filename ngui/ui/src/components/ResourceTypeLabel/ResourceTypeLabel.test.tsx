import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ResourceTypeLabel from "./ResourceTypeLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ResourceTypeLabel resourceInfo={{ resourceType: "resource_type" }} />
    </TestProvider>
  );
  root.unmount();
});

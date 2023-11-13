import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ResourceConstraints from "./ResourceConstraints";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ResourceConstraints resourceId="id" constraints={{}} poolPolicies={{}} isLoading={false} billingOnly={false} />
    </TestProvider>
  );
  root.unmount();
});

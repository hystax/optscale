import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ResourceLifecycleGlobalPoolPolicies from "./ResourceLifecycleGlobalPoolPolicies";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ResourceLifecycleGlobalPoolPolicies poolPolicies={[]} />
    </TestProvider>
  );
  root.unmount();
});

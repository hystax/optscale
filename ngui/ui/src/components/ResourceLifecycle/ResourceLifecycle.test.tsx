import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ResourceLifecycle from "./ResourceLifecycle";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ResourceLifecycle />
    </TestProvider>
  );
  root.unmount();
});

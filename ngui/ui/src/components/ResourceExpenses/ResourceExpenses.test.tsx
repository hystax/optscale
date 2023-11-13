import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ResourceExpenses from "./ResourceExpenses";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ResourceExpenses firstSeen={1622473475} lastSeen={1654687344} resourceId="e3272af1-cedd-4c5e-a318-197e4ea61b57" />
    </TestProvider>
  );
  root.unmount();
});

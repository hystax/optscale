import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ResourceCountBreakdown from "./ResourceCountBreakdown";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ResourceCountBreakdown countKeys={[]} counts={{}} breakdown={{}} appliedRange={{}} />
    </TestProvider>
  );
  root.unmount();
});

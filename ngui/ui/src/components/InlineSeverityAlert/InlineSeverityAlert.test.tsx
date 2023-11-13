import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import InlineSeverityAlert from "./InlineSeverityAlert";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <InlineSeverityAlert messageId="test" />
    </TestProvider>
  );
  root.unmount();
});

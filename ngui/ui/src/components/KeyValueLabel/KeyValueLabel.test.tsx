import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import KeyValueLabel from "./KeyValueLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <KeyValueLabel keyMessageId="name" value="value" />
    </TestProvider>
  );
  root.unmount();
});

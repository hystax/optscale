import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import TextBlock from "./TextBlock";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <TextBlock messageId="test" />
    </TestProvider>
  );
  root.unmount();
});

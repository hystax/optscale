import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Tooltip from "./Tooltip";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Tooltip title="title">
        <span>Content</span>
      </Tooltip>
    </TestProvider>
  );
  root.unmount();
});

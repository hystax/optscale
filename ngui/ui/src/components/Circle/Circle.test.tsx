import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Circle from "./Circle";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Circle />
    </TestProvider>
  );
  root.unmount();
});

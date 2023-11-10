import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Day from "./Day";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Day />
    </TestProvider>
  );
  root.unmount();
});

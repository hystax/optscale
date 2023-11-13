import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Tour from "./Tour";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Tour />
    </TestProvider>
  );
  root.unmount();
});

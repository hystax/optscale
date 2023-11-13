import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Ellipsis from "./Ellipsis";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Ellipsis />
    </TestProvider>
  );
  root.unmount();
});

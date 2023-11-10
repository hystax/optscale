import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import PoolsOverview from "./PoolsOverview";

it("renders without crashing without caption", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <PoolsOverview />
    </TestProvider>
  );
  root.unmount();
});

import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import PoolTypesDescription from "./PoolTypesDescription";

it("renders with action", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <PoolTypesDescription />
    </TestProvider>
  );
  root.unmount();
});

import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Environments from "./Environments";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Environments environments={[]} onUpdateActivity={() => {}} entityId="123" />
    </TestProvider>
  );
  root.unmount();
});

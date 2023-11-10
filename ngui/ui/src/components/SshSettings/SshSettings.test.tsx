import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import SshSettings from "./SshSettings";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <SshSettings />
    </TestProvider>
  );
  root.unmount();
});

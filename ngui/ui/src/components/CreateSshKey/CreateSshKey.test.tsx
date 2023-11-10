import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import CreateSshKey from "./CreateSshKey";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CreateSshKey />
    </TestProvider>
  );
  root.unmount();
});

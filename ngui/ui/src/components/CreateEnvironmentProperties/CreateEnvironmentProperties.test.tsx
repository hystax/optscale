import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import CreateEnvironmentProperties from "./CreateEnvironmentProperties";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CreateEnvironmentProperties environmentId="" existingProperties={[]} />
    </TestProvider>
  );
  root.unmount();
});

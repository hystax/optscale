import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import EnvironmentProperties from "./EnvironmentProperties";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <EnvironmentProperties environmentId="id" properties={[]} />
    </TestProvider>
  );
  root.unmount();
});

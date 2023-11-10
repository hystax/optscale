import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ResourceName from "./ResourceName";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ResourceName nama="name" />
    </TestProvider>
  );
  root.unmount();
});

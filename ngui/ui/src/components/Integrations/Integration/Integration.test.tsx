import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Integration from "./Integration";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Integration title={<div>title</div>} blocks={[<div key="block">block</div>]} id="integrationId" />
    </TestProvider>
  );
  root.unmount();
});

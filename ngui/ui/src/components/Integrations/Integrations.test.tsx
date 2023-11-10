import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Integrations from "./Integrations";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider state={{ organizationId: "organizationId" }}>
      <Integrations />
    </TestProvider>
  );
  root.unmount();
});

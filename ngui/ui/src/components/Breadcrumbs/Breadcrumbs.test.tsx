import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Breadcrumbs from "./Breadcrumbs";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Breadcrumbs>
        <span>Path 1</span>
        <span>Path 2</span>
      </Breadcrumbs>
    </TestProvider>
  );
  root.unmount();
});

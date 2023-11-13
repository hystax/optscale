import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import CollapsableMenuDrawer from "./CollapsableMenuDrawer";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CollapsableMenuDrawer />
    </TestProvider>
  );
  root.unmount();
});

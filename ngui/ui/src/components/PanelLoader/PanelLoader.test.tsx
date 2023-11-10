import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import PanelLoader from "./PanelLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <PanelLoader />
    </TestProvider>
  );
  root.unmount();
});

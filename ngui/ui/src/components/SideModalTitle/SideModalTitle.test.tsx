import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import SideModalTitle from "./SideModalTitle";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <SideModalTitle />
    </TestProvider>
  );
  root.unmount();
});

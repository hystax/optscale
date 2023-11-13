import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import BIExport from "./BIExport";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <BIExport />
    </TestProvider>
  );
  root.unmount();
});

import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import BIExportsTable from "./BIExportsTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <BIExportsTable exports={[]} />
    </TestProvider>
  );
  root.unmount();
});

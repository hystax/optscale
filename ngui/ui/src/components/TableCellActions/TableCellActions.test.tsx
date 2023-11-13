import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import TableCellActions from "./TableCellActions";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <TableCellActions items={[]} />
    </TestProvider>
  );
  root.unmount();
});

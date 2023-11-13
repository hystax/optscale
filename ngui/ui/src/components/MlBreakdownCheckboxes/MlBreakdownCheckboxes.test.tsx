import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MlBreakdownCheckboxes from "./MlBreakdownCheckboxes";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlBreakdownCheckboxes selectedBreakdowns={[]} colorsMap={{}} breakdownConfig={{}} onChange={vi.fn} />
    </TestProvider>
  );
  root.unmount();
});

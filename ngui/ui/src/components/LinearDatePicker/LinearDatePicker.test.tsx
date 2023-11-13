import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import LinearDatePicker from "./LinearDatePicker";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <LinearDatePicker selectedRange={{}} onSelectedRangeChange={vi.fn} ranges={[]} />
    </TestProvider>
  );
  root.unmount();
});

import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import DateRangePicker from "./DateRangePicker";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <DateRangePicker messageId="hystax" />
    </TestProvider>
  );
  root.unmount();
});

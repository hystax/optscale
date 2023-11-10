import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import QuickDatePickerValues from "./QuickDatePickerValues";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <QuickDatePickerValues titleMessageId="setToNow" items={[]} />
    </TestProvider>
  );
  root.unmount();
});

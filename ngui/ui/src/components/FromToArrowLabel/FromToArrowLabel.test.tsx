import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import FromToArrowLabel from "./FromToArrowLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <FromToArrowLabel from="from" to="to" />
    </TestProvider>
  );
  root.unmount();
});

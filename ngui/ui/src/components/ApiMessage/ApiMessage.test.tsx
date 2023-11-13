import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ApiMessage from "./ApiMessage";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ApiMessage code="OEXXX" />
    </TestProvider>
  );
  root.unmount();
});

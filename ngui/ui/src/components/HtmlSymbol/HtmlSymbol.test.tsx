import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import HtmlSymbol from "./HtmlSymbol";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <HtmlSymbol />
    </TestProvider>
  );
  root.unmount();
});

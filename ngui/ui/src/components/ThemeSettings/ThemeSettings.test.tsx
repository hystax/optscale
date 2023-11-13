import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ThemeSettings from "./ThemeSettings";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ThemeSettings />
    </TestProvider>
  );
  root.unmount();
});

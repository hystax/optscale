import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ActionBarResourceNameTitleText from "./ActionBarResourceNameTitleText";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ActionBarResourceNameTitleText />
    </TestProvider>
  );
  root.unmount();
});

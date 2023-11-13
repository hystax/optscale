import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import CopyText from "./CopyText";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CopyText text="text">text</CopyText>
    </TestProvider>
  );
  root.unmount();
});

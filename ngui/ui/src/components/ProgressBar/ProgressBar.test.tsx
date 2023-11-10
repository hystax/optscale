import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ProgressBar from "./ProgressBar";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ProgressBar />
    </TestProvider>
  );
  root.unmount();
});

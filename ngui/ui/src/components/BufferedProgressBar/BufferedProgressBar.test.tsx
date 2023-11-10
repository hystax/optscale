import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import BufferedProgressBar from "./BufferedProgressBar";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <BufferedProgressBar />
    </TestProvider>
  );
  root.unmount();
});

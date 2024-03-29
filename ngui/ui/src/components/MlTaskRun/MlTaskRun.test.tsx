import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MlTaskRun from "./MlTaskRun";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlTaskRun run={{}} />
    </TestProvider>
  );
  root.unmount();
});

import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MlEditTaskMetrics from "./MlEditTaskMetrics";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlEditTaskMetrics metrics={[]} onAttachChange={vi.fn} />
    </TestProvider>
  );
  root.unmount();
});

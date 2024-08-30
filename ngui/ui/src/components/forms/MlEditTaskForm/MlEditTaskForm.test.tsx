import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MlEditTaskForm from "./MlEditTaskForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlEditTaskForm task={{}} employees={[]} onSubmit={vi.fn} onCancel={vi.fn} />
    </TestProvider>
  );
  root.unmount();
});

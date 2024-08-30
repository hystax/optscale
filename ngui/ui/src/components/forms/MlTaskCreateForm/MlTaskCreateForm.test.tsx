import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MlTaskCreateForm from "./MlTaskCreateForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlTaskCreateForm onSubmit={vi.fn} onCancel={vi.fn} />
    </TestProvider>
  );
  root.unmount();
});

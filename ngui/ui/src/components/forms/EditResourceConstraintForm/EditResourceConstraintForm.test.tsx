import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import EditResourceConstraintForm from "./EditResourceConstraintForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <EditResourceConstraintForm
        constraintType="ttl"
        constraintLimit={0}
        constraintId="id"
        onSubmit={vi.fn}
        onSuccess={vi.fn}
        onCancel={vi.fn}
      />
    </TestProvider>
  );
  root.unmount();
});

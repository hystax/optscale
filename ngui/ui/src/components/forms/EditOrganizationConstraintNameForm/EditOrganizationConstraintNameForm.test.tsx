import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import EditOrganizationConstraintNameForm from "./EditOrganizationConstraintNameForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <EditOrganizationConstraintNameForm defaultName="" onCancel={vi.fn} onSubmit={vi.fn} />
    </TestProvider>
  );
  root.unmount();
});

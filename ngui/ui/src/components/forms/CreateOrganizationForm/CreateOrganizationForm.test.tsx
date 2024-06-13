import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import CreateOrganizationForm from "./CreateOrganizationForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CreateOrganizationForm onSubmit={vi.fn} onCancel={vi.fn} />
    </TestProvider>
  );
  root.unmount();
});

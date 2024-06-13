import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import RenameDataSourceForm from "./RenameDataSourceForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <RenameDataSourceForm name="name" onSubmit={vi.fn} onCancel={vi.fn} />
    </TestProvider>
  );
  root.unmount();
});

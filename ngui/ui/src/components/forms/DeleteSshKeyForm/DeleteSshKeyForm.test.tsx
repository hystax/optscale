import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import DeleteSshKeyForm from "./DeleteSshKeyForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <DeleteSshKeyForm />
    </TestProvider>
  );
  root.unmount();
});

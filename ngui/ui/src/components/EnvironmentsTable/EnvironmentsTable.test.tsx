import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import EnvironmentsTable from "./EnvironmentsTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <EnvironmentsTable data={[]} onUpdateActivity={() => {}} entityId="123" />
    </TestProvider>
  );
  root.unmount();
});

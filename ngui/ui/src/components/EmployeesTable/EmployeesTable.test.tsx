import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import EmployeesTable from "./EmployeesTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <EmployeesTable employees={[]} />
    </TestProvider>
  );
  root.unmount();
});

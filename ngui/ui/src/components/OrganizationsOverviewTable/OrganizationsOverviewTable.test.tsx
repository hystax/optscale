import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import OrganizationsOverviewTable from "./OrganizationsOverviewTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <OrganizationsOverviewTable data={[]} />
    </TestProvider>
  );
  root.unmount();
});

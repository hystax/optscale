import { createRoot } from "react-dom/client";
import { k8sRightsizingRelativeDates } from "components/RelativeDateTimePicker";
import TestProvider from "tests/TestProvider";
import K8sRightsizingTable from "./K8sRightsizingTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <K8sRightsizingTable namespaces={[]} definedRanges={k8sRightsizingRelativeDates} />
    </TestProvider>
  );
  root.unmount();
});

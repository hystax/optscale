import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ResourcePaidNetworkTrafficList from "./ResourcePaidNetworkTrafficList";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ResourcePaidNetworkTrafficList trafficExpenses={[]} />
    </TestProvider>
  );
  root.unmount();
});

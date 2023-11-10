import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import PoolsTable from "./PoolsTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <PoolsTable
        poolId="random-unit-id"
        rootPool={{ id: "random-unit-id", children: [] }}
        isLoadingProps={{ isGetPoolLoading: false, isGetPoolAllowedActionsLoading: false }}
      />
    </TestProvider>
  );
  root.unmount();
});

import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import { POOL_TYPE_BUDGET } from "utils/constants";
import PoolTypeIcon from "./PoolTypeIcon";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <PoolTypeIcon type={POOL_TYPE_BUDGET} />
    </TestProvider>
  );
  root.unmount();
});

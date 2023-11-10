import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import { COST_MODEL_TYPES } from "utils/constants";
import UpdateCostModelWarning from "./UpdateCostModelWarning";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <UpdateCostModelWarning costModelType={COST_MODEL_TYPES.K8S} />
    </TestProvider>
  );
  root.unmount();
});

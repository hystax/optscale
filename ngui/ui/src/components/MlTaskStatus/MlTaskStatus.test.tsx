import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import { ML_TASK_STATUS } from "utils/constants";
import MlTaskStatus from "./MlTaskStatus";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlTaskStatus status={ML_TASK_STATUS.CREATED} />
    </TestProvider>
  );
  root.unmount();
});

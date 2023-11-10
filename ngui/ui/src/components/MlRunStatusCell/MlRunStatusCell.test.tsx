import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import { ML_RUN_STATUS } from "utils/constants";
import MlRunStatusCell from "./MlRunStatusCell";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlRunStatusCell status={ML_RUN_STATUS.COMPLETED} />
    </TestProvider>
  );
  root.unmount();
});

import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import { ML_APPLICATION_STATUS } from "utils/constants";
import MlRunStatus from "./MlRunStatus";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlRunStatus status={ML_APPLICATION_STATUS.CREATED} />
    </TestProvider>
  );
  root.unmount();
});

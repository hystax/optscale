import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import { ML_MODEL_STATUS } from "utils/constants";
import MlModelStatus from "./MlModelStatus";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlModelStatus status={ML_MODEL_STATUS.CREATED} />
    </TestProvider>
  );
  root.unmount();
});

import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import { ML_APPLICATION_STATUS } from "utils/constants";
import MlApplicationStatusLabel from "./MlApplicationStatusLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlApplicationStatusLabel status={ML_APPLICATION_STATUS.CREATED} />
    </TestProvider>
  );
  root.unmount();
});

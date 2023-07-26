import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MlRunsetConfiguration from "./MlRunsetConfiguration";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlRunsetConfiguration />
    </TestProvider>
  );
  root.unmount();
});

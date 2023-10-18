import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MlModelRun from "./MlModelRun";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlModelRun run={{}} />
    </TestProvider>
  );
  root.unmount();
});

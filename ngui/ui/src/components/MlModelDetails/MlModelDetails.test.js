import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MlModelDetails from "./MlModelDetails";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlModelDetails model={{}} isLoading />
    </TestProvider>,
    div
  );
  root.unmount();
});

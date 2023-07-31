import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import EnvironmentCostModelForm from "./EnvironmentCostModelForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <EnvironmentCostModelForm onSubmit={jest.fn} onCancel={jest.fn} defaultHourlyPrice={0} />
    </TestProvider>
  );
  root.unmount();
});

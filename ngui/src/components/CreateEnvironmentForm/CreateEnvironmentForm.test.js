import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import CreateEnvironmentForm from "./CreateEnvironmentForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CreateEnvironmentForm onSubmit={jest.fn} onCancel={jest.fn} />
    </TestProvider>
  );
  root.unmount();
});

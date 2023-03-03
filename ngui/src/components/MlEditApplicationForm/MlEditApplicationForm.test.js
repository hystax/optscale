import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MlEditApplicationForm from "./MlEditApplicationForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlEditApplicationForm application={{}} employees={[]} onSubmit={jest.fn} onCancel={jest.fn} />
    </TestProvider>
  );
  root.unmount();
});

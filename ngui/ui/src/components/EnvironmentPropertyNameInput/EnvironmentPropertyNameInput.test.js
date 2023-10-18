import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import EnvironmentPropertyNameInput from "./EnvironmentPropertyNameInput";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <EnvironmentPropertyNameInput name="" register={vi.fn} />
    </TestProvider>
  );
  root.unmount();
});
